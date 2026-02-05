"""
Upload Endpoint / Endpoint de Subida
====================================

File upload endpoint for JSON and PDF files.
Endpoint de subida de archivos JSON y PDF.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, File, UploadFile

from src.api.exceptions import FileTooLargeError, InvalidFileTypeError, TooManyFilesError
from src.api.schemas.responses import ErrorResponse
from src.api.schemas.upload import FileInfo, UploadData, UploadResponse
from src.services.file_service import file_service

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_EXTENSIONS = {".json", ".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILES = 50


@router.post(
    "/upload",
    response_model=UploadResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Upload Files",
    description="Sube archivos JSON o PDF para procesamiento / Upload JSON or PDF files for processing",
)
async def upload_files(
    files: list[UploadFile] = File(..., description="Archivos a subir / Files to upload"),
) -> UploadResponse:
    """
    Upload JSON or PDF files for processing.
    Sube archivos JSON o PDF para procesamiento.

    Limits / Límites:
    - Maximum 50 files per request / Máximo 50 archivos por petición
    - Maximum 10MB per file / Máximo 10MB por archivo
    - Only .json and .pdf allowed / Solo .json y .pdf permitidos

    Args / Argumentos:
        files: List of files to upload / Lista de archivos a subir

    Returns / Retorna:
        UploadResponse with upload details / Detalles del upload

    Raises / Lanza:
        TooManyFilesError: If more than 50 files / Si más de 50 archivos
        InvalidFileTypeError: If invalid extension / Si extensión inválida
        FileTooLargeError: If file > 10MB / Si archivo > 10MB
    """
    # Validate file count
    if len(files) > MAX_FILES:
        raise TooManyFilesError(count=len(files), max_files=MAX_FILES)

    # Validate and read each file
    validated_files: list[dict[str, Any]] = []
    for file in files:
        # Validate extension
        ext = Path(file.filename or "").suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise InvalidFileTypeError(
                filename=file.filename or "unknown",
                allowed=list(ALLOWED_EXTENSIONS),
            )

        # Read and validate size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise FileTooLargeError(
                filename=file.filename or "unknown",
                max_size_mb=MAX_FILE_SIZE // (1024 * 1024),
            )

        validated_files.append(
            {
                "file": file,
                "content": content,
                "name": file.filename or f"file_{len(validated_files)}",
                "size": len(content),
                "type": ext[1:],  # Remove the dot
            }
        )

    # Save files
    upload_id = str(uuid4())
    saved_files = await file_service.save_upload(upload_id, validated_files)

    logger.info(
        "Upload %s: %d files, total %d bytes",
        upload_id,
        len(saved_files),
        sum(f["size"] for f in saved_files),
    )

    return UploadResponse(
        success=True,
        message="Archivos subidos correctamente / Files uploaded successfully",
        data=UploadData(
            upload_id=upload_id,
            files=[FileInfo(**f) for f in saved_files],
            total_files=len(saved_files),
            expires_at=datetime.utcnow() + timedelta(hours=24),
        ),
    )
