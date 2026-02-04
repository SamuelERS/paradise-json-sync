"""
API Module / Módulo del API
===========================

FastAPI API module with routes, schemas, and exception handlers.
Módulo del API FastAPI con rutas, esquemas y manejadores de excepciones.
"""

from src.api.exceptions import (
    APIException,
    FileTooLargeError,
    InvalidFileTypeError,
    JobNotCompletedError,
    JobNotFoundError,
    TooManyFilesError,
    UploadNotFoundError,
    setup_exception_handlers,
)
from src.api.routes import download, health, process, status, upload

__all__ = [
    # Routes
    "download",
    "health",
    "process",
    "status",
    "upload",
    # Exceptions
    "APIException",
    "UploadNotFoundError",
    "JobNotFoundError",
    "JobNotCompletedError",
    "InvalidFileTypeError",
    "FileTooLargeError",
    "TooManyFilesError",
    "setup_exception_handlers",
]
