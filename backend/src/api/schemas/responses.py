"""
Response Schemas / Esquemas de Respuesta
========================================

Common response schemas for API endpoints.
Esquemas de respuesta comunes para endpoints del API.
"""

from datetime import datetime

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """
    Error response schema / Esquema de respuesta de error.

    Attributes / Atributos:
        success: Always False / Siempre False
        error: Error code / Código de error
        message: Human-readable message / Mensaje legible
    """

    success: bool = False
    error: str
    message: str


class HealthResponse(BaseModel):
    """
    Health check response / Respuesta de health check.

    Attributes / Atributos:
        status: Server status / Estado del servidor
        version: API version / Versión del API
        timestamp: Current timestamp / Timestamp actual
        services: Status of dependent services / Estado de servicios dependientes
    """

    status: str
    version: str
    timestamp: datetime
    services: dict[str, str]
