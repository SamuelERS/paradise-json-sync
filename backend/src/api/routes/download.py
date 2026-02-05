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

from src.api.exceptions import JobNotCompletedError, JobNotFoundError
from src.api.schemas.responses import ErrorResponse
from src.core.excel_exporter import ExcelExporter
from src.core.json_processor import JSONProcessor
from src.services.job_service import job_service

logger = logging.getLogger(__name__)

router = APIRouter()

OUTPUT_DIR = Path("outputs")

CONTENT_TYPES = {
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "csv": "text/csv",
    "pdf": "application/pdf",
    "json": "application/json",
}


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

    The job must be in 'completed' status.
    El trabajo debe estar en estado 'completed'.

    Args / Argumentos:
        job_id: Job identifier / Identificador del trabajo

    Returns / Retorna:
        FileResponse with the result file / Archivo de resultado

    Raises / Lanza:
        JobNotFoundError: If job_id not found / Si no se encuentra el trabajo
        JobNotCompletedError: If job not completed / Si el trabajo no está completado
    """
    job = await job_service.get_job(job_id)

    if not job:
        raise JobNotFoundError(job_id)

    if job["status"] != "completed":
        raise JobNotCompletedError(job_id, job["status"])

    output_path = job["result"]["output_path"]
    output_format = job["output_format"]
    filename = job["result"]["output_file"]

    logger.info("Download requested for job %s: %s", job_id, filename)

    return FileResponse(
        path=output_path,
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
    Descarga el archivo Excel de resultado de un trabajo completado.

    If the job was processed with a different format, generates Excel on demand.
    Si el trabajo se procesó con otro formato, genera el Excel bajo demanda.

    Args / Argumentos:
        job_id: Job identifier / Identificador del trabajo

    Returns / Retorna:
        FileResponse with Excel file / Archivo Excel

    Raises / Lanza:
        JobNotFoundError: If job_id not found / Si no se encuentra el trabajo
        JobNotCompletedError: If job not completed / Si el trabajo no está completado
    """
    job = await job_service.get_job(job_id)

    if not job:
        raise JobNotFoundError(job_id)

    if job["status"] != "completed":
        raise JobNotCompletedError(job_id, job["status"])

    original_path = Path(job["result"]["output_path"])
    filename = f"consolidado_{job_id}.xlsx"

    # Check if the original file is already an Excel
    if job["output_format"] == "xlsx" and original_path.suffix.lower() == ".xlsx":
        logger.info("Excel download requested for job %s (original format)", job_id)
        return FileResponse(
            path=str(original_path),
            media_type=CONTENT_TYPES["xlsx"],
            filename=filename,
        )

    # Need to generate Excel from the original data
    logger.info(
        "Excel download requested for job %s - generating from %s format",
        job_id,
        job["output_format"],
    )

    xlsx_path = OUTPUT_DIR / f"reporte_{job_id}.xlsx"

    # If Excel already generated for this job, return it
    if xlsx_path.exists():
        logger.info("Returning cached Excel for job %s", job_id)
        return FileResponse(
            path=str(xlsx_path),
            media_type=CONTENT_TYPES["xlsx"],
            filename=filename,
        )

    # Generate Excel from original upload files
    from src.services.file_service import file_service

    upload_id = job["upload_id"]
    files = await file_service.get_files(upload_id)

    if not files:
        raise JobNotFoundError(
            f"Upload files not found for job {job_id}. "
            "Los archivos originales ya no están disponibles."
        )

    # Process files to get invoices
    json_processor = JSONProcessor()
    invoices = []

    for file_info in files:
        if file_info["type"] == "json":
            try:
                invoice = json_processor.process_file(file_info["path"])
                invoices.append(invoice)
            except Exception as e:
                logger.warning("Error processing %s for Excel: %s", file_info["name"], e)

    if not invoices:
        raise JobNotFoundError(
            f"No valid invoices found for job {job_id}. "
            "No se encontraron facturas válidas."
        )

    # Generate Excel
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
    Descarga el archivo PDF de resultado de un trabajo completado.

    If the job was processed with a different format, generates PDF on demand.
    Si el trabajo se procesó con otro formato, genera el PDF bajo demanda.

    Args / Argumentos:
        job_id: Job identifier / Identificador del trabajo

    Returns / Retorna:
        FileResponse with PDF file / Archivo PDF

    Raises / Lanza:
        JobNotFoundError: If job_id not found / Si no se encuentra el trabajo
        JobNotCompletedError: If job not completed / Si el trabajo no está completado
    """
    job = await job_service.get_job(job_id)

    if not job:
        raise JobNotFoundError(job_id)

    if job["status"] != "completed":
        raise JobNotCompletedError(job_id, job["status"])

    original_path = Path(job["result"]["output_path"])
    filename = f"consolidado_{job_id}.pdf"

    # Check if the original file is already a PDF
    if job["output_format"] == "pdf" and original_path.suffix.lower() == ".pdf":
        logger.info("PDF download requested for job %s (original format)", job_id)
        return FileResponse(
            path=str(original_path),
            media_type=CONTENT_TYPES["pdf"],
            filename=filename,
        )

    # Need to generate PDF from the original data
    # Re-process the files to generate PDF
    logger.info(
        "PDF download requested for job %s - generating from %s format",
        job_id,
        job["output_format"],
    )

    pdf_path = OUTPUT_DIR / f"reporte_{job_id}.pdf"

    # If PDF already generated for this job, return it
    if pdf_path.exists():
        logger.info("Returning cached PDF for job %s", job_id)
        return FileResponse(
            path=str(pdf_path),
            media_type=CONTENT_TYPES["pdf"],
            filename=filename,
        )

    # Generate PDF from original upload files
    from src.services.file_service import file_service

    upload_id = job["upload_id"]
    files = await file_service.get_files(upload_id)

    if not files:
        raise JobNotFoundError(
            f"Upload files not found for job {job_id}. "
            "Los archivos originales ya no están disponibles."
        )

    # Process files to get invoices
    json_processor = JSONProcessor()
    invoices = []

    for file_info in files:
        if file_info["type"] == "json":
            try:
                invoice = json_processor.process_file(file_info["path"])
                invoices.append(invoice)
            except Exception as e:
                logger.warning("Error processing %s for PDF: %s", file_info["name"], e)

    if not invoices:
        raise JobNotFoundError(
            f"No valid invoices found for job {job_id}. "
            "No se encontraron facturas válidas."
        )

    # Generate PDF
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
    Descarga el archivo JSON de resultado de un trabajo completado.

    If the job was processed with a different format, generates JSON on demand.
    Si el trabajo se procesó con otro formato, genera el JSON bajo demanda.

    Args / Argumentos:
        job_id: Job identifier / Identificador del trabajo

    Returns / Retorna:
        FileResponse with JSON file / Archivo JSON

    Raises / Lanza:
        JobNotFoundError: If job_id not found / Si no se encuentra el trabajo
        JobNotCompletedError: If job not completed / Si el trabajo no está completado
    """
    job = await job_service.get_job(job_id)

    if not job:
        raise JobNotFoundError(job_id)

    if job["status"] != "completed":
        raise JobNotCompletedError(job_id, job["status"])

    original_path = Path(job["result"]["output_path"])
    filename = f"consolidado_{job_id}.json"

    # Check if the original file is already a JSON
    if job["output_format"] == "json" and original_path.suffix.lower() == ".json":
        logger.info("JSON download requested for job %s (original format)", job_id)
        return FileResponse(
            path=str(original_path),
            media_type=CONTENT_TYPES["json"],
            filename=filename,
        )

    # Need to generate JSON from the original data
    logger.info(
        "JSON download requested for job %s - generating from %s format",
        job_id,
        job["output_format"],
    )

    json_path = OUTPUT_DIR / f"reporte_{job_id}.json"

    # If JSON already generated for this job, return it
    if json_path.exists():
        logger.info("Returning cached JSON for job %s", job_id)
        return FileResponse(
            path=str(json_path),
            media_type=CONTENT_TYPES["json"],
            filename=filename,
        )

    # Generate JSON from original upload files
    from src.services.file_service import file_service

    upload_id = job["upload_id"]
    files = await file_service.get_files(upload_id)

    if not files:
        raise JobNotFoundError(
            f"Upload files not found for job {job_id}. "
            "Los archivos originales ya no están disponibles."
        )

    # Process files to get invoices
    json_processor = JSONProcessor()
    invoices = []

    for file_info in files:
        if file_info["type"] == "json":
            try:
                invoice = json_processor.process_file(file_info["path"])
                invoices.append(invoice)
            except Exception as e:
                logger.warning("Error processing %s for JSON: %s", file_info["name"], e)

    if not invoices:
        raise JobNotFoundError(
            f"No valid invoices found for job {job_id}. "
            "No se encontraron facturas válidas."
        )

    # Generate JSON
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
