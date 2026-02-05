"""
Health Endpoint / Endpoint de Salud
===================================

Health check endpoint for monitoring.
Endpoint de verificación de salud para monitoreo.
"""

from datetime import datetime

from fastapi import APIRouter

from src.api.schemas.responses import HealthResponse

router = APIRouter()

VERSION = "1.0.0"


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Verifica el estado del servidor / Check server status",
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    Endpoint de verificación de salud.

    Used by CI/CD for smoke tests.
    Usado por CI/CD para pruebas de humo.

    Returns / Retorna:
        HealthResponse with server status / Estado del servidor
    """
    return HealthResponse(
        status="healthy",
        version=VERSION,
        timestamp=datetime.utcnow(),
        services={
            "storage": "ok",
            "processing": "ok",
        },
    )
