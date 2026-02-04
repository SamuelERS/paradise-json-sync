"""
Upload Schemas / Esquemas de Upload
===================================

Schemas for file upload endpoint.
Esquemas para endpoint de subida de archivos.
"""

from datetime import datetime

from pydantic import BaseModel


class FileInfo(BaseModel):
    """
    File information / Información de archivo.

    Attributes / Atributos:
        name: File name / Nombre del archivo
        size: File size in bytes / Tamaño en bytes
        type: File type (json or pdf) / Tipo de archivo
    """

    name: str
    size: int
    type: str


class UploadData(BaseModel):
    """
    Upload response data / Datos de respuesta de upload.

    Attributes / Atributos:
        upload_id: Unique upload identifier / Identificador único
        files: List of uploaded files / Lista de archivos subidos
        total_files: Total file count / Cantidad total de archivos
        expires_at: Expiration timestamp / Timestamp de expiración
    """

    upload_id: str
    files: list[FileInfo]
    total_files: int
    expires_at: datetime


class UploadResponse(BaseModel):
    """
    Upload endpoint response / Respuesta del endpoint de upload.

    Attributes / Atributos:
        success: Operation success / Éxito de la operación
        message: Response message / Mensaje de respuesta
        data: Upload data / Datos del upload
    """

    success: bool
    message: str
    data: UploadData
