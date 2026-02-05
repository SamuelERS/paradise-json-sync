"""
Download Endpoint / Endpoint de Descarga
========================================

Result file download endpoint.
Endpoint de descarga de archivos de resultado.
"""

import logging
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

from src.api.exceptions import APIException, JobNotCompletedError, JobNotFoundError
from src.api.schemas.responses import ErrorResponse
from src.core.excel_exporter import ExcelExporter
from src.core.json_processor import JSONProcessor
from src.services.job_service import job_service


class PathTraversalError(APIException):
    """Path traversal attempt detected / Intento de path traversal detectado."""

    def __init__(self) -> None:
        super().__init__(
            error="PATH_TRAVERSAL_BLOCKED",
            message="Invalid file path / Ruta de archivo inválida",
            status_code=403,
        )

logger = logging.getLogger(__name__)

router = APIRouter()

OUTPUT_DIR = Path("outputs").resolve()


def validate_output_path(path: Path) -> bool:
    """
    Validate that a path is within OUTPUT_DIR to prevent path traversal.
    Valida que un path esté dentro de OUTPUT_DIR para prevenir path traversal.

    Args / Argumentos:
        path: Path to validate / Path a validar

    Returns / Retorna:
        True if path is safe / True si el path es seguro
    """
    try:
        resolved_path = path.resolve()
        # SECURITY: Only use is_relative_to, not startswith which can be bypassed
        # SEGURIDAD: Solo usar is_relative_to, no startswith que puede ser evadido
        return resolved_path.is_relative_to(OUTPUT_DIR)
    except (ValueError, RuntimeError):
        return False


CONTENT_TYPES = {
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "csv": "text/csv",
    "pdf": "application/pdf",
    "json": "application/json",
}


# ── Common helpers / Helpers comunes ──────────────────────────────────────


async def _get_completed_job(job_id: str) -> dict:
    """
    Fetch and validate a completed job.
    Obtiene y valida un trabajo completado.

    Raises / Lanza:
        JobNotFoundError: If job not found / Si no se encuentra
        JobNotCompletedError: If not completed / Si no está completado
    """
    job = await job_service.get_job(job_id)

    if not job:
        raise JobNotFoundError(job_id)

    if job.get("status") != "completed":
        raise JobNotCompletedError(job_id, job.get("status", "unknown"))

    return job


def _get_validated_output_path(job: dict, job_id: str) -> Path:
    """
    Extract and validate the output path from a job result.
    Extrae y valida el path de salida del resultado de un trabajo.

    Raises / Lanza:
        JobNotFoundError: If output path missing / Si falta el path
        PathTraversalError: If path outside OUTPUT_DIR / Si el path está fuera
    """
    result = job.get("result", {})
    output_path_str = result.get("output_path")
    if not output_path_str:
        raise JobNotFoundError(f"Output path not found for job {job_id}")

    output_path = Path(output_path_str)

    # SECURITY: Validate path before any file operation
    if not validate_output_path(output_path):
        logger.warning("Path traversal attempt blocked for job_id=%s", job_id)
        raise PathTraversalError()

    return output_path


async def _get_invoices_for_job(job: dict, job_id: str, target_format: str) -> list:
    """
    Re-process upload files to extract invoices for format conversion.
    Re-procesa archivos de upload para extraer facturas para conversión de formato.

    Raises / Lanza:
        JobNotFoundError: If upload files unavailable / Si los archivos no están disponibles
    """
    from src.services.file_service import file_service

    upload_id = job.get("upload_id")
    if not upload_id:
        raise JobNotFoundError(f"Upload ID not found for job {job_id}")
    files = await file_service.get_files(upload_id)

    if not files:
        raise JobNotFoundError(
            f"Upload files not found for job {job_id}. "
            "Los archivos originales ya no están disponibles."
        )

    json_processor = JSONProcessor()
    invoices = []

    for file_info in files:
        if file_info["type"] == "json":
            try:
                invoice = json_processor.process_file(file_info["path"])
                invoices.append(invoice)
            except Exception as e:
                logger.warning(
                    "Error processing %s for %s: %s",
                    file_info["name"],
                    target_format,
                    e,
                )

    if not invoices:
        raise JobNotFoundError(
            f"No valid invoices found for job {job_id}. "
            "No se encontraron facturas válidas."
        )

    return invoices


# ── Endpoints ─────────────────────────────────────────────────────────────


@router.get(
    "/download/{job_id}",
    responses={
        200: {
            "content": {"application/octet-stream": {}},
            "description": "File download / Descarga de archivo",
        },
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Download Result",
    description="Descarga el archivo de resultados / Download result file",
)
async def download_result(job_id: str) -> FileResponse:
    """
    Download the result file for a completed job.
    Descarga el archivo de resultado de un trabajo completado.
    """
    job = await _get_completed_job(job_id)
    output_path = _get_validated_output_path(job, job_id)

    output_format = job.get("output_format", "xlsx")
    result = job.get("result", {})
    filename = result.get("output_file", f"result_{job_id}")

    logger.info("Download requested for job %s: %s", job_id, filename)

    return FileResponse(
        path=str(output_path),
        media_type=CONTENT_TYPES.get(output_format, "application/octet-stream"),
        filename=filename,
    )


@router.get(
    "/download/excel/{job_id}",
    responses={
        200: {
            "content": {CONTENT_TYPES["xlsx"]: {}},
            "description": "Excel file download / Descarga de archivo Excel",
        },
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Download Excel Result",
    description="Descarga el resultado en formato Excel / Download result as Excel",
)
async def download_excel(job_id: str) -> FileResponse:
    """
    Download the Excel result file for a completed job.
    If the job was processed with a different format, generates Excel on demand.
    """
    job = await _get_completed_job(job_id)
    original_path = _get_validated_output_path(job, job_id)
    filename = f"consolidado_{job_id}.xlsx"

    # Return original if already Excel
    if job.get("output_format") == "xlsx" and original_path.suffix.lower() == ".xlsx":
        logger.info("Excel download for job %s (original format)", job_id)
        return FileResponse(
            path=str(original_path),
            media_type=CONTENT_TYPES["xlsx"],
            filename=filename,
        )

    # Return cached conversion if available
    xlsx_path = OUTPUT_DIR / f"reporte_{job_id}.xlsx"
    if xlsx_path.exists():
        logger.info("Returning cached Excel for job %s", job_id)
        return FileResponse(
            path=str(xlsx_path),
            media_type=CONTENT_TYPES["xlsx"],
            filename=filename,
        )

    # Generate Excel from upload files
    invoices = await _get_invoices_for_job(job, job_id, "Excel")
    exporter = ExcelExporter()
    exporter.export_to_excel(
        invoices,
        str(xlsx_path),
        include_summary=job.get("options", {}).get("include_summary", True),
    )

    logger.info("Generated Excel for job %s with %d invoices", job_id, len(invoices))

    return FileResponse(
        path=str(xlsx_path),
        media_type=CONTENT_TYPES["xlsx"],
        filename=filename,
    )


@router.get(
    "/download/pdf/{job_id}",
    responses={
        200: {
            "content": {CONTENT_TYPES["pdf"]: {}},
            "description": "PDF file download / Descarga de archivo PDF",
        },
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Download PDF Result",
    description="Descarga el resultado en formato PDF / Download result as PDF",
)
async def download_pdf(job_id: str) -> FileResponse:
    """
    Download the PDF result file for a completed job.
    If the job was processed with a different format, generates PDF on demand.
    """
    job = await _get_completed_job(job_id)
    original_path = _get_validated_output_path(job, job_id)
    filename = f"consolidado_{job_id}.pdf"
    output_format = job.get("output_format", "xlsx")

    # Return original if already PDF
    if output_format == "pdf" and original_path.suffix.lower() == ".pdf":
        logger.info("PDF download for job %s (original format)", job_id)
        return FileResponse(
            path=str(original_path),
            media_type=CONTENT_TYPES["pdf"],
            filename=filename,
        )

    # Return cached conversion if available
    pdf_path = OUTPUT_DIR / f"reporte_{job_id}.pdf"
    if pdf_path.exists():
        logger.info("Returning cached PDF for job %s", job_id)
        return FileResponse(
            path=str(pdf_path),
            media_type=CONTENT_TYPES["pdf"],
            filename=filename,
        )

    # Generate PDF from upload files
    invoices = await _get_invoices_for_job(job, job_id, "PDF")
    exporter = ExcelExporter()
    exporter.export_to_pdf(
        invoices,
        str(pdf_path),
        include_summary=job.get("options", {}).get("include_summary", True),
    )

    logger.info("Generated PDF for job %s with %d invoices", job_id, len(invoices))

    return FileResponse(
        path=str(pdf_path),
        media_type=CONTENT_TYPES["pdf"],
        filename=filename,
    )


@router.get(
    "/download/json/{job_id}",
    responses={
        200: {
            "content": {CONTENT_TYPES["json"]: {}},
            "description": "JSON file download / Descarga de archivo JSON",
        },
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Download JSON Result",
    description="Descarga el resultado en formato JSON consolidado / Download result as consolidated JSON",
)
async def download_json(job_id: str) -> FileResponse:
    """
    Download the JSON result file for a completed job.
    If the job was processed with a different format, generates JSON on demand.
    """
    job = await _get_completed_job(job_id)
    original_path = _get_validated_output_path(job, job_id)
    filename = f"consolidado_{job_id}.json"
    output_format = job.get("output_format", "xlsx")

    # Return original if already JSON
    if output_format == "json" and original_path.suffix.lower() == ".json":
        logger.info("JSON download for job %s (original format)", job_id)
        return FileResponse(
            path=str(original_path),
            media_type=CONTENT_TYPES["json"],
            filename=filename,
        )

    # Return cached conversion if available
    json_path = OUTPUT_DIR / f"reporte_{job_id}.json"
    if json_path.exists():
        logger.info("Returning cached JSON for job %s", job_id)
        return FileResponse(
            path=str(json_path),
            media_type=CONTENT_TYPES["json"],
            filename=filename,
        )

    # Generate JSON from upload files
    invoices = await _get_invoices_for_job(job, job_id, "JSON")
    exporter = ExcelExporter()
    exporter.export_to_json(
        invoices,
        str(json_path),
        include_metadata=True,
    )

    logger.info("Generated JSON for job %s with %d invoices", job_id, len(invoices))

    return FileResponse(
        path=str(json_path),
        media_type=CONTENT_TYPES["json"],
        filename=filename,
    )
