"""
Status Schemas / Esquemas de Estado
===================================

Schemas for status endpoint.
Esquemas para endpoint de estado.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class JobResult(BaseModel):
    """
    Job result data / Datos de resultado del trabajo.

    Attributes / Atributos:
        total_invoices: Number of processed invoices / Facturas procesadas
        total_amount: Sum of invoice totals / Suma de totales
        output_file: Output filename / Nombre del archivo de salida
        output_path: Full path to output / Ruta completa del archivo
    """

    total_invoices: int
    total_amount: float
    output_file: str
    output_path: Optional[str] = None


class JobData(BaseModel):
    """
    Job status data / Datos de estado del trabajo.

    Attributes / Atributos:
        job_id: Job identifier / Identificador del trabajo
        status: Current status / Estado actual (pending, processing, completed, failed)
        progress: Progress percentage / Porcentaje de progreso
        current_step: Current processing step / Paso actual de procesamiento
        result: Job result if completed / Resultado si completado
        error: Error message if failed / Mensaje de error si falló
        started_at: Start timestamp / Timestamp de inicio
        completed_at: Completion timestamp / Timestamp de finalización
        failed_at: Failure timestamp / Timestamp de fallo
    """

    job_id: str
    status: str
    progress: int = 0
    current_step: Optional[str] = None
    result: Optional[JobResult] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None


class StatusResponse(BaseModel):
    """
    Status endpoint response / Respuesta del endpoint de estado.

    Attributes / Atributos:
        success: Operation success / Éxito de la operación
        data: Job status data / Datos de estado del trabajo
    """

    success: bool
    data: JobData
