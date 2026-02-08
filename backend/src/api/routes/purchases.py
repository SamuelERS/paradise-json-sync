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

_BASICO_COLS = ["control_number", "document_type", "issue_date", "supplier_name", "total"]
_COMPLETO_COLS = [
    "control_number", "document_number", "document_type", "issue_date",
    "supplier_name", "supplier_nit", "supplier_nrc", "subtotal",
    "total_taxable", "total_exempt", "total_non_subject", "tax", "total",
]
_CONTADOR_COLS = [
    "control_number", "document_type", "issue_date", "supplier_name",
    "supplier_nit", "total_taxable", "total_exempt", "tax", "total",
]
COLUMN_PROFILES = {
    "basico": {"name": "Basico", "description": "Solo campos esenciales", "columns": _BASICO_COLS},
    "completo": {"name": "Completo", "description": "Todos los campos disponibles", "columns": _COMPLETO_COLS},
    "contador": {"name": "Contador", "description": "Campos fiscales para contabilidad", "columns": _CONTADOR_COLS},
}

_COL_DEFS = [
    ("control_number", "N Control", "identificacion"),
    ("document_number", "Cod Generacion", "identificacion"),
    ("document_type", "Tipo Doc", "identificacion"),
    ("issue_date", "Fecha", "identificacion"),
    ("supplier_name", "Proveedor", "proveedor"),
    ("supplier_nit", "NIT Proveedor", "proveedor"),
    ("supplier_nrc", "NRC Proveedor", "proveedor"),
    ("subtotal", "Subtotal", "montos"),
    ("total_taxable", "Gravado", "montos"),
    ("total_exempt", "Exento", "montos"),
    ("total_non_subject", "No Sujeto", "montos"),
    ("tax", "IVA", "montos"),
    ("total", "Total", "montos"),
]
ALL_COLUMNS = [PurchaseColumnInfo(id=c[0], label=c[1], category=c[2]) for c in _COL_DEFS]
VALID_COLUMN_IDS = {c.id for c in ALL_COLUMNS}

_FMT_DEFS = [
    ("DTE_STANDARD", "DTE Estandar (Hacienda)", "Formato oficial del Ministerio de Hacienda"),
    ("DTE_VARIANT_A", "DTE Variante A", "Items en 'detalle' en vez de 'cuerpoDocumento'"),
    ("DTE_VARIANT_B", "DTE Variante B", "Estructura con campos renombrados"),
    ("GENERIC_FLAT", "JSON Plano Generico", "Formato plano sin estructura DTE"),
    ("PDF_EXTRACTED", "PDF (texto extraido)", "Datos extraidos de factura en PDF"),
]
SUPPORTED_FORMATS = [PurchaseFormatInfo(id=f[0], name=f[1], description=f[2]) for f in _FMT_DEFS]


def _validate_file_content(filename: str, ext: str, content: bytes) -> None:
    """Validate file content matches its extension. / Valida contenido del archivo."""
    if ext == ".pdf" and not content.startswith(b"%PDF"):
        raise InvalidFileTypeError(
            filename=filename, allowed=list(ALLOWED_EXTENSIONS),
            detail="No es un PDF valido / Not a valid PDF",
        )
    elif ext == ".json":
        try:
            json.loads(content.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise InvalidFileTypeError(
                filename=filename, allowed=list(ALLOWED_EXTENSIONS),
                detail="JSON invalido / Invalid JSON",
            )


async def _validate_and_read_files(
    files: List[UploadFile],
) -> tuple[list[dict], int, int]:
    """Validate and read uploaded files. / Valida y lee archivos subidos."""
    validated: list[dict] = []
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
        _validate_file_content(file.filename or "unknown", ext, content)
        if ext == ".pdf":
            pdf_count += 1
        elif ext == ".json":
            json_count += 1
        validated.append({
            "content": content,
            "name": file.filename or f"file_{len(validated)}",
            "size": len(content),
            "type": ext[1:],
        })
    return validated, json_count, pdf_count


@router.post(
    "/upload",
    response_model=PurchaseUploadResponse,
    responses={400: {"model": ErrorResponse}, 429: {"description": "Rate limit exceeded"}},
    summary="Upload Purchase Files",
)
@limiter.limit("10/minute")
async def upload_purchase_files(
    request: Request,
    files: List[UploadFile] = File(..., description="Archivos de compras"),
) -> PurchaseUploadResponse:
    """Upload purchase invoice files (JSON/PDF). / Sube archivos de compra."""
    if len(files) > MAX_FILES:
        raise TooManyFilesError(count=len(files), max_files=MAX_FILES)

    validated_files, json_count, pdf_count = await _validate_and_read_files(files)
    upload_id = str(uuid4())
    saved_files = await file_service.save_upload(upload_id, validated_files)
    logger.info(
        "Purchase upload %s: %d files (%d json, %d pdf)",
        upload_id, len(saved_files), json_count, pdf_count,
    )
    return PurchaseUploadResponse(
        success=True,
        message=f"{len(saved_files)} archivos subidos correctamente",
        data=PurchaseUploadData(
            upload_id=upload_id,
            files=[FileInfo(**f) for f in saved_files],
            total_files=len(saved_files),
            json_count=json_count, pdf_count=pdf_count,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        ),
    )


def _validate_custom_columns(
    request_data: PurchaseProcessRequest,
) -> JSONResponse | None:
    """Validate custom columns if profile is custom. / Valida columnas custom."""
    if request_data.column_profile != "custom":
        return None
    if not request_data.custom_columns:
        return JSONResponse(status_code=400, content={
            "success": False, "error": "INVALID_REQUEST",
            "message": "custom_columns requerido con perfil custom / custom_columns required with custom profile",
        })
    invalid_cols = [c for c in request_data.custom_columns if c not in VALID_COLUMN_IDS]
    if invalid_cols:
        return JSONResponse(status_code=400, content={
            "success": False, "error": "INVALID_REQUEST",
            "message": f"Columnas invalidas: {invalid_cols} / Invalid columns: {invalid_cols}",
        })
    return None


@router.post("/process", status_code=202, summary="Process Purchases")
async def process_purchases(
    request_data: PurchaseProcessRequest,
    background_tasks: BackgroundTasks,
) -> dict:
    """Start async processing of purchases. / Inicia procesamiento asincrono."""
    upload = await file_service.get_upload(request_data.upload_id)
    if not upload:
        raise UploadNotFoundError(request_data.upload_id)

    col_error = _validate_custom_columns(request_data)
    if col_error:
        return col_error

    job_id = str(uuid4())
    await job_service.create_job(
        job_id=job_id, upload_id=request_data.upload_id,
        output_format=request_data.output_format,
        options=request_data.options.model_dump(),
    )
    background_tasks.add_task(_run_processing, job_id, upload, request_data)
    return {
        "success": True,
        "message": "Procesamiento iniciado / Processing started",
        "data": {
            "job_id": job_id, "status": "processing",
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
        all_paths = [
            f["path"] for f in files
            if f.get("type") in ("json", "pdf")
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
            file_paths=all_paths,
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


@router.get("/status/{job_id}", summary="Purchase Status")
async def get_purchase_status(job_id: str) -> dict:
    """Get processing status. / Obtiene estado de procesamiento."""
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


@router.get("/download/{job_id}", summary="Download Purchase Result")
async def download_purchase_result(job_id: str) -> FileResponse:
    """Download result file. / Descarga el archivo de resultado."""
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


@router.get("/formats", summary="List Formats")
async def list_formats() -> dict:
    """List supported formats. / Lista formatos soportados."""
    return {
        "formats": [f.model_dump() for f in SUPPORTED_FORMATS]
    }


@router.get("/columns", summary="List Columns")
async def list_columns() -> dict:
    """List columns and profiles. / Lista columnas y perfiles."""
    return {
        "profiles": COLUMN_PROFILES,
        "all_columns": [c.model_dump() for c in ALL_COLUMNS],
    }
