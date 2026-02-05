"""
API Exceptions / Excepciones del API
====================================

Custom exceptions and exception handlers for the API.
Excepciones personalizadas y manejadores para el API.
"""

import logging
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.formparsers import MultiPartException

logger = logging.getLogger(__name__)


class APIException(Exception):
    """
    Custom API exception / Excepción personalizada del API.

    Attributes / Atributos:
        error: Error code / Código de error
        message: Human-readable message / Mensaje legible
        status_code: HTTP status code / Código de estado HTTP
    """

    def __init__(
        self,
        error: str,
        message: str,
        status_code: int = 400,
    ) -> None:
        self.error = error
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UploadNotFoundError(APIException):
    """Upload not found exception / Excepción de upload no encontrado."""

    def __init__(self, upload_id: str) -> None:
        super().__init__(
            error="UPLOAD_NOT_FOUND",
            message=f"Upload not found: {upload_id} / Upload no encontrado",
            status_code=404,
        )


class JobNotFoundError(APIException):
    """Job not found exception / Excepción de trabajo no encontrado."""

    def __init__(self, job_id: str) -> None:
        super().__init__(
            error="JOB_NOT_FOUND",
            message=f"Job not found: {job_id} / Trabajo no encontrado",
            status_code=404,
        )


class JobNotCompletedError(APIException):
    """Job not completed exception / Excepción de trabajo no completado."""

    def __init__(self, job_id: str, status: str) -> None:
        super().__init__(
            error="JOB_NOT_COMPLETED",
            message=f"Job {job_id} is not completed (status: {status}) / Trabajo no completado",
            status_code=400,
        )


class InvalidFileTypeError(APIException):
    """Invalid file type exception / Excepción de tipo de archivo inválido."""

    def __init__(self, filename: str, allowed: List[str], detail: Optional[str] = None) -> None:
        base_message = f"File {filename}: only {', '.join(allowed)} allowed / Solo se permiten {', '.join(allowed)}"
        message = f"{base_message}. {detail}" if detail else base_message
        super().__init__(
            error="INVALID_FILE_TYPE",
            message=message,
            status_code=400,
        )


class FileTooLargeError(APIException):
    """File too large exception / Excepción de archivo muy grande."""

    def __init__(self, filename: str, max_size_mb: int) -> None:
        super().__init__(
            error="FILE_TOO_LARGE",
            message=f"File {filename}: max {max_size_mb}MB / Máximo {max_size_mb}MB",
            status_code=400,
        )


class TooManyFilesError(APIException):
    """Too many files exception / Excepción de demasiados archivos."""

    def __init__(self, count: int, max_files: int) -> None:
        super().__init__(
            error="TOO_MANY_FILES",
            message=f"Too many files: {count} (max {max_files}) / Demasiados archivos",
            status_code=400,
        )


def _too_many_files_response(message: str) -> JSONResponse:
    """
    Create standardized response for too many files error.
    Crea respuesta estandarizada para error de demasiados archivos.
    """
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": "TOO_MANY_FILES",
            "message": message,
        },
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Setup exception handlers for the FastAPI app.
    Configura manejadores de excepciones para la app FastAPI.

    Args / Argumentos:
        app: FastAPI application instance / Instancia de la aplicación
    """

    @app.exception_handler(APIException)
    async def api_exception_handler(
        request: Request,
        exc: APIException,
    ) -> JSONResponse:
        """Handle custom API exceptions / Maneja excepciones del API."""
        logger.warning(
            "API Exception: %s - %s (path: %s)",
            exc.error,
            exc.message,
            request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.error,
                "message": exc.message,
            },
        )

    @app.exception_handler(MultiPartException)
    async def multipart_exception_handler(
        request: Request,
        exc: MultiPartException,
    ) -> JSONResponse:
        """
        Handle Starlette MultiPartException for form parsing errors.
        Maneja MultiPartException de Starlette para errores de parseo de formularios.
        """
        message = str(exc)

        # Convert "Too many files" error to our custom format
        # Convertir error "Too many files" a nuestro formato personalizado
        if "Too many files" in message:
            return _too_many_files_response(message)

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "FORM_PARSE_ERROR",
                "message": message,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        """Handle HTTP exceptions / Maneja excepciones HTTP."""
        detail = exc.detail

        if isinstance(detail, dict):
            return JSONResponse(
                status_code=exc.status_code,
                content={"success": False, **detail},
            )

        # Convert Starlette's "Too many files" error to our custom format
        # Convertir el error "Too many files" de Starlette a nuestro formato
        detail_str = str(detail)
        if "Too many files" in detail_str:
            return _too_many_files_response(detail_str)

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": "HTTP_ERROR",
                "message": detail_str,
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        """
        Handle Starlette HTTP exceptions (e.g., multipart parsing errors).
        Maneja excepciones HTTP de Starlette (e.g., errores de parseo multipart).
        """
        detail = str(exc.detail) if exc.detail else ""
        if "Too many files" in detail:
            return _too_many_files_response(detail)

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": "HTTP_ERROR",
                "message": detail or "HTTP error",
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle unexpected exceptions / Maneja excepciones inesperadas."""
        logger.exception(
            "Unhandled exception on %s: %s",
            request.url.path,
            str(exc),
        )
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "INTERNAL_ERROR",
                "message": "Internal server error / Error interno del servidor",
            },
        )
