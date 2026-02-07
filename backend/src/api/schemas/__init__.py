"""
API Schemas / Esquemas del API
==============================

Pydantic schemas for API request/response validation.
Esquemas Pydantic para validación de peticiones/respuestas del API.
"""

from src.api.schemas.process import (
    ProcessData,
    ProcessOptions,
    ProcessRequest,
    ProcessResponse,
)
from src.api.schemas.purchases import (
    ProcessingResult,
    PurchaseColumnInfo,
    PurchaseFormatInfo,
    PurchaseProcessOptions,
    PurchaseProcessRequest,
    PurchaseUploadData,
    PurchaseUploadResponse,
)
from src.api.schemas.responses import ErrorResponse, HealthResponse
from src.api.schemas.status import JobData, JobResult, StatusResponse
from src.api.schemas.upload import FileInfo, UploadData, UploadResponse

__all__ = [
    # Upload
    "FileInfo",
    "UploadData",
    "UploadResponse",
    # Process
    "ProcessOptions",
    "ProcessRequest",
    "ProcessData",
    "ProcessResponse",
    # Status
    "JobResult",
    "JobData",
    "StatusResponse",
    # Responses
    "ErrorResponse",
    "HealthResponse",
    # Purchases
    "PurchaseProcessOptions",
    "PurchaseProcessRequest",
    "PurchaseUploadData",
    "PurchaseUploadResponse",
    "PurchaseFormatInfo",
    "PurchaseColumnInfo",
    "ProcessingResult",
]
