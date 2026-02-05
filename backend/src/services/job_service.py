"""
Job Service / Servicio de Trabajos
==================================

Service for managing processing jobs.
Servicio para gestión de trabajos de procesamiento.
"""

import logging
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class JobService:
    """
    Job management service / Servicio de gestión de trabajos.

    Handles job creation, status updates, and completion tracking.
    Maneja creación de trabajos, actualizaciones de estado y seguimiento.

    Attributes / Atributos:
        _jobs: In-memory job registry / Registro de trabajos en memoria
    """

    def __init__(self) -> None:
        """
        Initialize the job service.
        Inicializa el servicio de trabajos.
        """
        self._jobs: dict[str, dict] = {}
        logger.debug("JobService initialized")

    async def create_job(
        self,
        job_id: str,
        upload_id: str,
        output_format: str,
        options: Optional[dict] = None,
    ) -> dict:
        """
        Create a new processing job.
        Crea un nuevo trabajo de procesamiento.

        Args / Argumentos:
            job_id: Unique job identifier / Identificador único
            upload_id: Associated upload ID / ID del upload asociado
            output_format: Output format (xlsx, csv, pdf) / Formato de salida
            options: Processing options / Opciones de procesamiento

        Returns / Retorna:
            Created job data / Datos del trabajo creado
        """
        job = {
            "job_id": job_id,
            "upload_id": upload_id,
            "output_format": output_format,
            "options": options or {},
            "status": "pending",
            "progress": 0,
            "current_step": None,
            "result": None,
            "error": None,
            "created_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
            "failed_at": None,
        }

        self._jobs[job_id] = job
        logger.info("Created job: %s for upload: %s", job_id, upload_id)

        return job

    async def get_job(self, job_id: str) -> Optional[dict]:
        """
        Get job by ID.
        Obtiene trabajo por ID.

        Args / Argumentos:
            job_id: Job identifier / Identificador del trabajo

        Returns / Retorna:
            Job data dict or None / Dict de datos o None
        """
        return self._jobs.get(job_id)

    async def update_progress(
        self,
        job_id: str,
        progress: int,
        step: Optional[str] = None,
    ) -> bool:
        """
        Update job progress.
        Actualiza progreso del trabajo.

        Args / Argumentos:
            job_id: Job identifier / Identificador del trabajo
            progress: Progress percentage (0-100) / Porcentaje de progreso
            step: Current step description / Descripción del paso actual

        Returns / Retorna:
            True if updated / True si se actualizó
        """
        if job_id not in self._jobs:
            return False

        job = self._jobs[job_id]
        job["status"] = "processing"
        job["progress"] = min(max(progress, 0), 100)

        if step:
            job["current_step"] = step

        if not job["started_at"]:
            job["started_at"] = datetime.utcnow()

        logger.debug(
            "Job %s progress: %d%% - %s",
            job_id,
            progress,
            step or "N/A",
        )

        return True

    async def complete_job(
        self,
        job_id: str,
        output_path: str,
        invoices: list,
    ) -> bool:
        """
        Mark job as completed.
        Marca trabajo como completado.

        Args / Argumentos:
            job_id: Job identifier / Identificador del trabajo
            output_path: Path to output file / Ruta al archivo de salida
            invoices: List of processed invoices / Lista de facturas procesadas

        Returns / Retorna:
            True if completed / True si se completó
        """
        if job_id not in self._jobs:
            return False

        job = self._jobs[job_id]

        # Calculate total amount
        total_amount = sum(
            float(inv.total) if isinstance(inv.total, Decimal) else inv.total for inv in invoices
        )

        job["status"] = "completed"
        job["progress"] = 100
        job["current_step"] = None
        job["completed_at"] = datetime.utcnow()
        job["result"] = {
            "total_invoices": len(invoices),
            "total_amount": total_amount,
            "output_file": Path(output_path).name,
            "output_path": output_path,
        }

        logger.info(
            "Job %s completed: %d invoices, total: %.2f",
            job_id,
            len(invoices),
            total_amount,
        )

        return True

    async def fail_job(self, job_id: str, error: str) -> bool:
        """
        Mark job as failed.
        Marca trabajo como fallido.

        Args / Argumentos:
            job_id: Job identifier / Identificador del trabajo
            error: Error message / Mensaje de error

        Returns / Retorna:
            True if marked as failed / True si se marcó como fallido
        """
        if job_id not in self._jobs:
            return False

        job = self._jobs[job_id]
        job["status"] = "failed"
        job["error"] = error
        job["failed_at"] = datetime.utcnow()

        logger.error("Job %s failed: %s", job_id, error)

        return True

    async def delete_job(self, job_id: str) -> bool:
        """
        Delete a job.
        Elimina un trabajo.

        Args / Argumentos:
            job_id: Job identifier / Identificador del trabajo

        Returns / Retorna:
            True if deleted / True si se eliminó
        """
        if job_id not in self._jobs:
            return False

        del self._jobs[job_id]
        logger.info("Deleted job: %s", job_id)

        return True

    def list_jobs(self, status: Optional[str] = None) -> list[dict]:
        """
        List all jobs, optionally filtered by status.
        Lista todos los trabajos, opcionalmente filtrados por estado.

        Args / Argumentos:
            status: Filter by status / Filtrar por estado

        Returns / Retorna:
            List of job dicts / Lista de dicts de trabajos
        """
        jobs = list(self._jobs.values())

        if status:
            jobs = [j for j in jobs if j["status"] == status]

        return jobs


# Global instance / Instancia global
job_service = JobService()
