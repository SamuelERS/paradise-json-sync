"""
API Routes / Rutas del API
==========================

FastAPI routers for all API endpoints.
Routers de FastAPI para todos los endpoints del API.
"""

from src.api.routes import download, health, process, status, upload

__all__ = [
    "download",
    "health",
    "process",
    "status",
    "upload",
]
