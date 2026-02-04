"""
Process Endpoint / Endpoint de Procesamiento
=============================================

File processing endpoint.
Endpoint de procesamiento de archivos.
"""

import logging
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks

from src.api.exceptions import UploadNotFoundError
from src.api.schemas.process import ProcessData, ProcessRequest, ProcessResponse
from src.api.schemas.responses import ErrorResponse
from src.core.data_validator import DataValidator
from src.core.excel_exporter import ExcelExporter
from src.core.json_processor import JSONProcessor
from src.services.file_service import file_service
from src.services.job_service import job_service

logger = logging.getLogger(__name__)

router = APIRouter()

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def estimate_time(file_count: int) -> int:
    """
    Estimate processing time in seconds.
    Estima tiempo de procesamiento en segundos.
    """
    return max(5, file_count * 2)


async def process_job_task(
    job_id: str,
    upload_id: str,
    output_format: str,
    options: dict,
) -> None:
    """
    Background task to process files.
    Tarea en segundo plano para procesar archivos.

    Args / Argumentos:
        job_id: Job identifier / Identificador del trabajo
        upload_id: Upload identifier / Identificador del upload
        output_format: Output format (xlsx, csv, pdf) / Formato de salida
        options: Processing options / Opciones de procesamiento
    """
    try:
        files = await file_service.get_files(upload_id)
        invoices = []

        json_processor = JSONProcessor()
        validator = DataValidator()

        # Process each file
        for i, file_info in enumerate(files):
            await job_service.update_progress(
                job_id,
                progress=int((i / len(files)) * 80),
                step=f"Procesando archivo {i + 1} de {len(files)} / Processing file {i + 1} of {len(files)}",
            )

            if file_info["type"] == "json":
                try:
                    invoice = json_processor.process_file(file_info["path"])
                    # Validate invoice
                    is_valid, errors = validator.validate_invoice(invoice)
                    if is_valid:
                        invoices.append(invoice)
                    else:
                        logger.warning(
                            "Invoice validation failed for %s: %s",
                            file_info["name"],
                            errors,
                        )
                except Exception as e:
                    logger.warning("Error processing %s: %s", file_info["name"], e)

        if not invoices:
            await job_service.fail_job(
                job_id,
                "No valid invoices found / No se encontraron facturas válidas",
            )
            return

        # Export
        await job_service.update_progress(
            job_id,
            progress=90,
            step="Generando reporte / Generating report",
        )

        exporter = ExcelExporter()
        output_filename = f"reporte_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{output_format}"
        output_path = OUTPUT_DIR / output_filename

        # Export based on format / Exportar según formato
        if output_format == "xlsx":
            exporter.export_to_excel(
                invoices,
                str(output_path),
                include_summary=options.get("include_summary", True),
            )
        elif output_format == "csv":
            exporter.export_to_csv(
                invoices,
                str(output_path),
            )
        elif output_format == "pdf":
            exporter.export_to_pdf(
                invoices,
                str(output_path),
                include_summary=options.get("include_summary", True),
            )
        elif output_format == "json":
            exporter.export_to_json(
                invoices,
                str(output_path),
            )
        else:
            raise ValueError(f"Unsupported format: {output_format}")

        # Complete job
        await job_service.complete_job(job_id, str(output_path), invoices)

        logger.info(
            "Job %s completed: %d invoices exported to %s",
            job_id,
            len(invoices),
            output_path,
        )

    except Exception as e:
        logger.exception("Job %s failed: %s", job_id, e)
        await job_service.fail_job(job_id, str(e))


@router.post(
    "/process",
    response_model=ProcessResponse,
    status_code=202,
    responses={404: {"model": ErrorResponse}},
    summary="Process Files",
    description="Inicia el procesamiento de archivos subidos / Start processing uploaded files",
)
async def process_files(
    request: ProcessRequest,
    background_tasks: BackgroundTasks,
) -> ProcessResponse:
    """
    Start processing uploaded files.
    Inicia el procesamiento de archivos subidos.

    The processing runs in the background. Use GET /api/status/{job_id}
    to check progress.

    El procesamiento se ejecuta en segundo plano. Use GET /api/status/{job_id}
    para consultar el progreso.

    Args / Argumentos:
        request: Process request with upload_id and options
        background_tasks: FastAPI background tasks handler

    Returns / Retorna:
        ProcessResponse with job details / Detalles del trabajo

    Raises / Lanza:
        UploadNotFoundError: If upload_id not found / Si no se encuentra el upload
    """
    # Verify upload exists
    upload = await file_service.get_upload(request.upload_id)
    if not upload:
        raise UploadNotFoundError(request.upload_id)

    # Create job
    job_id = str(uuid4())
    options_dict = request.options.model_dump() if request.options else {}

    await job_service.create_job(
        job_id=job_id,
        upload_id=request.upload_id,
        output_format=request.output_format,
        options=options_dict,
    )

    # Start background processing
    background_tasks.add_task(
        process_job_task,
        job_id,
        request.upload_id,
        request.output_format,
        options_dict,
    )

    logger.info(
        "Started job %s for upload %s (format: %s)",
        job_id,
        request.upload_id,
        request.output_format,
    )

    return ProcessResponse(
        success=True,
        message="Procesamiento iniciado / Processing started",
        data=ProcessData(
            job_id=job_id,
            status="processing",
            estimated_time=estimate_time(upload["total_files"]),
            created_at=datetime.utcnow(),
        ),
    )
