"""
Process Schemas / Esquemas de Procesamiento
============================================

Schemas for process endpoint.
Esquemas para endpoint de procesamiento.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ProcessOptions(BaseModel):
    """
    Processing options / Opciones de procesamiento.

    Attributes / Atributos:
        include_summary: Include summary sheet / Incluir hoja de resumen
        group_by: Group invoices by / Agrupar facturas por
    """

    include_summary: bool = True
    group_by: Literal["date", "vendor", "none"] = "none"


class ProcessRequest(BaseModel):
    """
    Process request body / Cuerpo de petición de proceso.

    Attributes / Atributos:
        upload_id: Upload ID to process / ID del upload a procesar
        output_format: Output file format / Formato de archivo de salida
        options: Processing options / Opciones de procesamiento
    """

    upload_id: str
    output_format: Literal["xlsx", "csv", "pdf", "json"] = "xlsx"
    options: ProcessOptions = Field(default_factory=ProcessOptions)


class ProcessData(BaseModel):
    """
    Process response data / Datos de respuesta de proceso.

    Attributes / Atributos:
        job_id: Job identifier / Identificador del trabajo
        status: Current status / Estado actual
        estimated_time: Estimated time in seconds / Tiempo estimado en segundos
        created_at: Creation timestamp / Timestamp de creación
    """

    job_id: str
    status: str
    estimated_time: int
    created_at: datetime


class ProcessResponse(BaseModel):
    """
    Process endpoint response / Respuesta del endpoint de proceso.

    Attributes / Atributos:
        success: Operation success / Éxito de la operación
        message: Response message / Mensaje de respuesta
        data: Process data / Datos del proceso
    """

    success: bool
    message: str
    data: ProcessData
