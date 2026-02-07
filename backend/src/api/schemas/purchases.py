"""
Purchase Schemas / Esquemas de Compras
=======================================

Pydantic schemas for purchase API request/response validation.
Esquemas Pydantic para validacion de peticiones/respuestas del API de compras.

This module provides / Este modulo provee:
- PurchaseProcessOptions: Processing options for purchases
- PurchaseProcessRequest: Request to start purchase processing
- PurchaseUploadData: Upload response data for purchases
- PurchaseUploadResponse: Upload endpoint response
- PurchaseFormatInfo: Information about a supported format
- PurchaseColumnInfo: Information about an available column
- ProcessingResult: Internal processing result model
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from src.api.schemas.upload import FileInfo


class PurchaseProcessOptions(BaseModel):
    """
    Purchase processing options / Opciones de procesamiento de compras.

    Attributes / Atributos:
        include_summary: Include summary sheet / Incluir hoja de resumen
        include_items_sheet: Include items detail / Incluir detalle items
        group_by: Grouping criteria / Criterio de agrupacion
        include_raw_data: Include original JSON / Incluir JSON original
    """

    include_summary: bool = True
    include_items_sheet: bool = True
    group_by: Literal["none", "supplier", "date", "type"] = "none"
    include_raw_data: bool = False


class PurchaseProcessRequest(BaseModel):
    """
    Request to start purchase processing.
    Peticion para iniciar procesamiento de compras.

    Attributes / Atributos:
        upload_id: ID of the previous upload / ID del upload previo
        output_format: Output file format / Formato de archivo de salida
        column_profile: Column profile / Perfil de columnas
        custom_columns: Custom column list / Lista de columnas custom
        options: Processing options / Opciones de procesamiento
    """

    upload_id: str
    output_format: Literal["xlsx", "csv", "pdf", "json"] = "xlsx"
    column_profile: Literal[
        "basico", "completo", "contador", "custom"
    ] = "completo"
    custom_columns: Optional[list[str]] = None
    options: PurchaseProcessOptions = Field(
        default_factory=PurchaseProcessOptions
    )


class PurchaseUploadData(BaseModel):
    """
    Purchase upload response data / Datos de respuesta de upload.

    Attributes / Atributos:
        upload_id: Unique upload identifier / Identificador unico
        files: List of uploaded files / Lista de archivos subidos
        total_files: Total file count / Cantidad total de archivos
        json_count: JSON file count / Cantidad de archivos JSON
        pdf_count: PDF file count / Cantidad de archivos PDF
        expires_at: Expiration timestamp / Timestamp de expiracion
    """

    upload_id: str
    files: list[FileInfo]
    total_files: int
    json_count: int
    pdf_count: int
    expires_at: datetime


class PurchaseUploadResponse(BaseModel):
    """
    Purchase upload endpoint response.
    Respuesta del endpoint de upload de compras.

    Attributes / Atributos:
        success: Operation success / Exito de la operacion
        message: Response message / Mensaje de respuesta
        data: Upload data / Datos del upload
    """

    success: bool = True
    message: str
    data: PurchaseUploadData


class PurchaseFormatInfo(BaseModel):
    """
    Information about a supported format.
    Informacion de un formato soportado.

    Attributes / Atributos:
        id: Format identifier / Identificador del formato
        name: Display name / Nombre para mostrar
        description: Format description / Descripcion del formato
    """

    id: str
    name: str
    description: str


class PurchaseColumnInfo(BaseModel):
    """
    Information about an available column.
    Informacion de una columna disponible.

    Attributes / Atributos:
        id: Column identifier / Identificador de la columna
        label: Display label / Etiqueta para mostrar
        category: Column category / Categoria de la columna
    """

    id: str
    label: str
    category: str


class ProcessingResult(BaseModel):
    """
    Internal processing result model.
    Modelo de resultado de procesamiento (uso interno).

    Attributes / Atributos:
        invoices: Processed invoices / Facturas procesadas
        invoice_count: Valid invoice count / Cantidad de facturas validas
        error_count: Error count / Cantidad de errores
        errors: List of errors / Lista de errores
        formats_summary: Format counts / Conteo de formatos
    """

    invoices: list = Field(default_factory=list)
    invoice_count: int = 0
    error_count: int = 0
    errors: list = Field(default_factory=list)
    formats_summary: dict = Field(default_factory=dict)
