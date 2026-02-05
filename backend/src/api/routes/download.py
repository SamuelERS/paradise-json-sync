"""
Download Endpoint / Endpoint de Descarga
========================================

Result file download endpoint.
Endpoint de descarga de archivos de resultado.
"""

import logging

from fastapi import APIRouter
from fastapi.responses import FileResponse

from src.api.exceptions import JobNotCompletedError, JobNotFoundError
from src.api.schemas.responses import ErrorResponse
from src.services.job_service import job_service

logger = logging.getLogger(__name__)

router = APIRouter()

CONTENT_TYPES = {
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "csv": "text/csv",
    "pdf": "application/pdf",
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

    output_path = job["result"]["output_path"]
    filename = f"consolidado_{job_id}.xlsx"

    logger.info("Excel download requested for job %s", job_id)

    return FileResponse(
        path=output_path,
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

    output_path = job["result"]["output_path"]
    filename = f"consolidado_{job_id}.pdf"

    logger.info("PDF download requested for job %s", job_id)

    return FileResponse(
        path=output_path,
        media_type=CONTENT_TYPES["pdf"],
        filename=filename,
    )
