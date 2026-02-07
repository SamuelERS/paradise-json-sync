"""
Purchase Endpoints / Endpoints de Compras
==========================================

API endpoints for purchase invoice processing.
Endpoints del API para procesamiento de facturas de compra.

This module provides / Este modulo provee:
- POST /upload: Upload JSON/PDF files for purchase processing
- POST /process: Start async processing of uploaded files
- GET /status/{job_id}: Check processing status
- GET /download/{job_id}: Download result file
- GET /formats: List supported invoice formats
- GET /columns: List available columns and profiles
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from uuid import uuid4

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    Request,
    UploadFile,
)
from fastapi.responses import FileResponse, JSONResponse

from src.api.exceptions import (
    FileTooLargeError,
    InvalidFileTypeError,
    JobNotCompletedError,
    JobNotFoundError,
    TooManyFilesError,
    UploadNotFoundError,
)
from src.api.schemas.purchases import (
    PurchaseColumnInfo,
    PurchaseFormatInfo,
    PurchaseProcessRequest,
    PurchaseUploadData,
    PurchaseUploadResponse,
)
from src.api.schemas.responses import ErrorResponse
from src.api.schemas.upload import FileInfo
from src.core.purchases.format_detector import DetectedFormat
from src.core.rate_limiter import limiter
from src.services.file_service import file_service
from src.services.job_service import job_service
from src.services.purchase_service import PurchaseProcessorService

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_EXTENSIONS = {".json", ".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILES = 10000

# Column profiles / Perfiles de columnas
COLUMN_PROFILES = {
    "basico": {
        "name": "Basico",
        "description": "Solo campos esenciales",
        "columns": [
            "control_number",
            "document_type",
            "issue_date",
            "supplier_name",
            "total",
        ],
    },
    "completo": {
        "name": "Completo",
        "description": "Todos los campos disponibles",
        "columns": [
            "control_number",
            "document_number",
            "document_type",
            "issue_date",
            "supplier_name",
            "supplier_nit",
            "supplier_nrc",
            "subtotal",
            "total_taxable",
            "total_exempt",
            "total_non_subject",
            "tax",
            "total",
        ],
    },
    "contador": {
        "name": "Contador",
        "description": "Campos fiscales para contabilidad",
        "columns": [
            "control_number",
            "document_type",
            "issue_date",
            "supplier_name",
            "supplier_nit",
            "total_taxable",
            "total_exempt",
            "tax",
            "total",
        ],
    },
}

ALL_COLUMNS = [
    PurchaseColumnInfo(
        id="control_number", label="N Control", category="identificacion"
    ),
    PurchaseColumnInfo(
        id="document_number", label="Cod Generacion", category="identificacion"
    ),
    PurchaseColumnInfo(
        id="document_type", label="Tipo Doc", category="identificacion"
    ),
    PurchaseColumnInfo(
        id="issue_date", label="Fecha", category="identificacion"
    ),
    PurchaseColumnInfo(
        id="supplier_name", label="Proveedor", category="proveedor"
    ),
    PurchaseColumnInfo(
        id="supplier_nit", label="NIT Proveedor", category="proveedor"
    ),
    PurchaseColumnInfo(
        id="supplier_nrc", label="NRC Proveedor", category="proveedor"
    ),
    PurchaseColumnInfo(
        id="subtotal", label="Subtotal", category="montos"
    ),
    PurchaseColumnInfo(
        id="total_taxable", label="Gravado", category="montos"
    ),
    PurchaseColumnInfo(
        id="total_exempt", label="Exento", category="montos"
    ),
    PurchaseColumnInfo(
        id="total_non_subject", label="No Sujeto", category="montos"
    ),
    PurchaseColumnInfo(
        id="tax", label="IVA", category="montos"
    ),
    PurchaseColumnInfo(
        id="total", label="Total", category="montos"
    ),
]

VALID_COLUMN_IDS = {c.id for c in ALL_COLUMNS}

# Format info / Informacion de formatos
SUPPORTED_FORMATS = [
    PurchaseFormatInfo(
        id="DTE_STANDARD",
        name="DTE Estandar (Hacienda)",
        description="Formato oficial del Ministerio de Hacienda",
    ),
    PurchaseFormatInfo(
        id="DTE_VARIANT_A",
        name="DTE Variante A",
        description="Items en 'detalle' en vez de 'cuerpoDocumento'",
    ),
    PurchaseFormatInfo(
        id="DTE_VARIANT_B",
        name="DTE Variante B",
        description="Estructura con campos renombrados",
    ),
    PurchaseFormatInfo(
        id="GENERIC_FLAT",
        name="JSON Plano Generico",
        description="Formato plano sin estructura DTE",
    ),
    PurchaseFormatInfo(
        id="PDF_EXTRACTED",
        name="PDF (texto extraido)",
        description="Datos extraidos de factura en PDF",
    ),
]


@router.post(
    "/upload",
    response_model=PurchaseUploadResponse,
    responses={
        400: {"model": ErrorResponse},
        429: {"description": "Rate limit exceeded"},
    },
    summary="Upload Purchase Files",
    description=(
        "Sube archivos JSON o PDF de compras / "
        "Upload purchase JSON or PDF files"
    ),
)
@limiter.limit("10/minute")
async def upload_purchase_files(
    request: Request,
    files: List[UploadFile] = File(
        ..., description="Archivos de compras / Purchase files"
    ),
) -> PurchaseUploadResponse:
    """
    Upload purchase invoice files (JSON/PDF).
    Sube archivos de facturas de compra (JSON/PDF).

    Args / Argumentos:
        request: HTTP request (required for rate limiter)
        files: List of files to upload

    Returns / Retorna:
        PurchaseUploadResponse with upload details

    Raises / Lanza:
        TooManyFilesError: If more than 10000 files
        InvalidFileTypeError: If invalid extension
        FileTooLargeError: If file > 10MB
    """
    if len(files) > MAX_FILES:
        raise TooManyFilesError(
            count=len(files), max_files=MAX_FILES
        )

    validated_files: list[dict] = []
    json_count = 0
    pdf_count = 0

    for file in files:
        ext = Path(file.filename or "").suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise InvalidFileTypeError(
                filename=file.filename or "unknown",
                allowed=list(ALLOWED_EXTENSIONS),
            )

        content = await file.read()
        await file.close()
        if len(content) > MAX_FILE_SIZE:
            raise FileTooLargeError(
                filename=file.filename or "unknown",
                max_size_mb=MAX_FILE_SIZE // (1024 * 1024),
            )

        if ext == ".pdf":
            if not content.startswith(b"%PDF"):
                raise InvalidFileTypeError(
                    filename=file.filename or "unknown",
                    allowed=list(ALLOWED_EXTENSIONS),
                    detail="No es un PDF valido / Not a valid PDF",
                )
            pdf_count += 1
        elif ext == ".json":
            try:
                json.loads(content.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                raise InvalidFileTypeError(
                    filename=file.filename or "unknown",
                    allowed=list(ALLOWED_EXTENSIONS),
                    detail="JSON invalido / Invalid JSON",
                )
            json_count += 1

        validated_files.append({
            "content": content,
            "name": file.filename or f"file_{len(validated_files)}",
            "size": len(content),
            "type": ext[1:],
        })

    upload_id = str(uuid4())
    saved_files = await file_service.save_upload(
        upload_id, validated_files
    )

    logger.info(
        "Purchase upload %s: %d files (%d json, %d pdf)",
        upload_id, len(saved_files), json_count, pdf_count,
    )

    return PurchaseUploadResponse(
        success=True,
        message=(
            f"{len(saved_files)} archivos subidos correctamente / "
            f"{len(saved_files)} files uploaded successfully"
        ),
        data=PurchaseUploadData(
            upload_id=upload_id,
            files=[FileInfo(**f) for f in saved_files],
            total_files=len(saved_files),
            json_count=json_count,
            pdf_count=pdf_count,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        ),
    )


@router.post(
    "/process",
    status_code=202,
    summary="Process Purchases",
    description=(
        "Inicia procesamiento asincrono / "
        "Start async purchase processing"
    ),
)
async def process_purchases(
    request_data: PurchaseProcessRequest,
    background_tasks: BackgroundTasks,
) -> dict:
    """
    Start async processing of uploaded purchase files.
    Inicia procesamiento asincrono de archivos de compra.

    Args / Argumentos:
        request_data: Processing configuration
        background_tasks: FastAPI background tasks

    Returns / Retorna:
        Dict with job_id and status

    Raises / Lanza:
        UploadNotFoundError: If upload_id not found
        APIException: If custom_columns invalid
    """
    upload = await file_service.get_upload(request_data.upload_id)
    if not upload:
        raise UploadNotFoundError(request_data.upload_id)

    if request_data.column_profile == "custom":
        if not request_data.custom_columns:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "INVALID_REQUEST",
                    "message": (
                        "custom_columns requerido con perfil custom / "
                        "custom_columns required with custom profile"
                    ),
                },
            )
        invalid_cols = [
            c for c in request_data.custom_columns
            if c not in VALID_COLUMN_IDS
        ]
        if invalid_cols:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "INVALID_REQUEST",
                    "message": (
                        f"Columnas invalidas: {invalid_cols} / "
                        f"Invalid columns: {invalid_cols}"
                    ),
                },
            )

    job_id = str(uuid4())
    await job_service.create_job(
        job_id=job_id,
        upload_id=request_data.upload_id,
        output_format=request_data.output_format,
        options=request_data.options.model_dump(),
    )

    background_tasks.add_task(
        _run_processing, job_id, upload, request_data
    )

    return {
        "success": True,
        "message": "Procesamiento iniciado / Processing started",
        "data": {
            "job_id": job_id,
            "status": "processing",
            "created_at": datetime.utcnow().isoformat(),
        },
    }


async def _run_processing(
    job_id: str,
    upload: dict,
    config: PurchaseProcessRequest,
) -> None:
    """
    Background task for processing purchases.
    Tarea en background para procesamiento de compras.
    """
    try:
        files = upload.get("files", [])
        json_paths = [
            f["path"] for f in files
            if f.get("type") == "json"
        ]

        async def progress_cb(
            current: int, total: int, msg: str
        ) -> None:
            pct = int((current / total) * 100) if total else 0
            await job_service.update_progress(
                job_id, pct, msg
            )

        service = PurchaseProcessorService()
        result = await service.process(
            file_paths=json_paths,
            config=config,
            progress_callback=progress_cb,
        )

        await job_service.update_progress(job_id, 100, "Completado")

        job = await job_service.get_job(job_id)
        if job:
            job["status"] = "completed"
            job["progress"] = 100
            job["completed_at"] = datetime.utcnow()
            job["result"] = {
                "invoice_count": result.invoice_count,
                "error_count": result.error_count,
                "errors": result.errors,
                "formats_summary": result.formats_summary,
            }

    except Exception as e:
        logger.error("Processing failed for job %s: %s", job_id, e)
        await job_service.fail_job(job_id, str(e))


@router.get(
    "/status/{job_id}",
    summary="Purchase Status",
    description=(
        "Consulta estado del procesamiento / "
        "Check processing status"
    ),
)
async def get_purchase_status(job_id: str) -> dict:
    """
    Get processing status for a purchase job.
    Obtiene estado de procesamiento de un job de compras.

    Args / Argumentos:
        job_id: Job identifier

    Returns / Retorna:
        Dict with job status and progress

    Raises / Lanza:
        JobNotFoundError: If job_id not found
    """
    job = await job_service.get_job(job_id)
    if not job:
        raise JobNotFoundError(job_id)

    return {
        "success": True,
        "data": {
            "job_id": job["job_id"],
            "status": job["status"],
            "progress": job["progress"],
            "step": job.get("current_step"),
            "result": job.get("result"),
            "error": job.get("error"),
            "created_at": (
                job["created_at"].isoformat()
                if job.get("created_at") else None
            ),
        },
    }


@router.get(
    "/download/{job_id}",
    summary="Download Purchase Result",
    description=(
        "Descarga el resultado / Download the result file"
    ),
)
async def download_purchase_result(job_id: str) -> FileResponse:
    """
    Download the result file for a completed job.
    Descarga el archivo de resultado de un job completado.

    Args / Argumentos:
        job_id: Job identifier

    Returns / Retorna:
        FileResponse with the generated file

    Raises / Lanza:
        JobNotFoundError: If job_id not found
        JobNotCompletedError: If job not completed
    """
    job = await job_service.get_job(job_id)
    if not job:
        raise JobNotFoundError(job_id)

    if job["status"] != "completed":
        raise JobNotCompletedError(job_id, job["status"])

    result = job.get("result", {})
    output_path = result.get("output_path")

    if not output_path or not Path(output_path).exists():
        raise JobNotCompletedError(job_id, "no_output_file")

    return FileResponse(
        path=output_path,
        filename=Path(output_path).name,
        media_type="application/octet-stream",
    )


@router.get(
    "/formats",
    summary="List Formats",
    description=(
        "Lista formatos soportados / "
        "List supported invoice formats"
    ),
)
async def list_formats() -> dict:
    """
    List supported purchase invoice formats.
    Lista formatos de factura de compra soportados.

    Returns / Retorna:
        Dict with list of supported formats
    """
    return {
        "formats": [f.model_dump() for f in SUPPORTED_FORMATS]
    }


@router.get(
    "/columns",
    summary="List Columns",
    description=(
        "Lista columnas y perfiles / "
        "List available columns and profiles"
    ),
)
async def list_columns() -> dict:
    """
    List available columns and column profiles.
    Lista columnas disponibles y perfiles de columnas.

    Returns / Retorna:
        Dict with profiles and all_columns
    """
    return {
        "profiles": COLUMN_PROFILES,
        "all_columns": [c.model_dump() for c in ALL_COLUMNS],
    }
