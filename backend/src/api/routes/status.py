"""
Status Endpoint / Endpoint de Estado
====================================

Job status endpoint.
Endpoint de estado de trabajos.
"""

import logging

from fastapi import APIRouter

from src.api.exceptions import JobNotFoundError
from src.api.schemas.responses import ErrorResponse
from src.api.schemas.status import JobData, JobResult, StatusResponse
from src.services.job_service import job_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/status/{job_id}",
    response_model=StatusResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get Job Status",
    description="Consulta el estado de un trabajo / Check job status",
)
async def get_status(job_id: str) -> StatusResponse:
    """
    Get job status by ID.
    Obtiene el estado de un trabajo por ID.

    Possible statuses / Estados posibles:
    - pending: Waiting to start / Esperando iniciar
    - processing: Currently processing / Procesando
    - completed: Finished successfully / Completado exitosamente
    - failed: Finished with error / Terminado con error

    Args / Argumentos:
        job_id: Job identifier / Identificador del trabajo

    Returns / Retorna:
        StatusResponse with job details / Detalles del trabajo

    Raises / Lanza:
        JobNotFoundError: If job_id not found / Si no se encuentra el trabajo
    """
    job = await job_service.get_job(job_id)

    if not job:
        raise JobNotFoundError(job_id)

    # Build result if completed
    result = None
    if job["result"]:
        result = JobResult(
            total_invoices=job["result"]["total_invoices"],
            total_amount=job["result"]["total_amount"],
            output_file=job["result"]["output_file"],
            output_path=job["result"].get("output_path"),
        )

    return StatusResponse(
        success=True,
        data=JobData(
            job_id=job["job_id"],
            status=job["status"],
            progress=job["progress"],
            current_step=job["current_step"],
            result=result,
            error=job["error"],
            started_at=job["started_at"],
            completed_at=job["completed_at"],
            failed_at=job["failed_at"],
        ),
    )
