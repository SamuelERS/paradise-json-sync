"""
Purchase Invoice Models / Modelos de Factura de Compra
======================================================

Pydantic models for purchase invoice data validation and serialization.
Modelos Pydantic para validacion y serializacion de datos de facturas de compra.

This module defines / Este modulo define:
- PurchaseDocumentType: Enum for DTE document types (9 types)
                        Enum para tipos de documento DTE (9 tipos)
- SupplierInfo: Supplier (issuer) information model
                Modelo de informacion del proveedor (emisor)
- PurchaseInvoiceItem: Individual line item in a purchase invoice
                       Item individual en una factura de compra
- PurchaseInvoice: Complete purchase invoice with header and items
                   Factura de compra completa con encabezado e items
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger(__name__)


class PurchaseDocumentType(str, Enum):
    """
    Purchase document type enumeration / Enumeracion de tipos de documento.

    DTE document types that can be received as purchases.
    Tipos de documento DTE que se pueden recibir como compras.

    Values / Valores:
    - FACTURA: Standard invoice (01) / Factura de Consumidor Final
    - CCF: Tax Credit Certificate (03) / Comprobante de Credito Fiscal
    - NOTA_CREDITO: Credit note (05) / Nota de Credito
    - NOTA_DEBITO: Debit note (06) / Nota de Debito
    - FACTURA_EXPORTACION: Export invoice (11) / Factura de Exportacion
    - SUJETO_EXCLUIDO: Excluded subject (14) / Factura Sujeto Excluido
    - COMPROBANTE_RETENCION: Retention receipt (07) / Comprobante de Retencion
    - COMPROBANTE_DONACION: Donation receipt (15) / Comprobante de Donacion
    - DESCONOCIDO: Unknown type / Tipo no reconocido
    """

    FACTURA = "factura"
    CCF = "ccf"
    NOTA_CREDITO = "nota_credito"
    NOTA_DEBITO = "nota_debito"
    FACTURA_EXPORTACION = "factura_exp"
    SUJETO_EXCLUIDO = "sujeto_excluido"
    COMPROBANTE_RETENCION = "retencion"
    COMPROBANTE_DONACION = "donacion"
    DESCONOCIDO = "desconocido"


class SupplierInfo(BaseModel):
    """
    Supplier information model / Modelo de informacion del proveedor.

    Represents the supplier (issuer) of a purchase invoice.
    Representa al proveedor (emisor) de una factura de compra.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Legal name / Nombre legal (razon social)",
    )
    commercial_name: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Commercial name / Nombre comercial",
    )
    nit: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Supplier NIT / NIT del proveedor",
    )
    nrc: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Supplier NRC / NRC del proveedor",
    )
    economic_activity: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Economic activity / Actividad economica",
    )
    address: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Full address / Direccion completa",
    )
    phone: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Phone number / Telefono",
    )
    email: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Email address / Correo electronico",
    )
    establishment_code: Optional[str] = Field(
        default=None,
        max_length=20,
        description=(
            "Establishment code / Codigo de establecimiento"
            " (codEstableMH)"
        ),
    )
    establishment_type: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Establishment type / Tipo de establecimiento",
    )

    class Config:
        """Pydantic configuration / Configuracion de Pydantic."""

        json_encoders = {Decimal: lambda v: float(v)}


class PurchaseInvoiceItem(BaseModel):
    """
    Purchase invoice line item / Item de linea de factura de compra.

    Represents a single product or service in a purchase invoice.
    Representa un producto o servicio individual en una factura de compra.
    """

    item_number: Optional[int] = Field(
        default=None,
        description="Item sequence number / Numero de item (numItem)",
    )
    product_code: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Product code / Codigo del producto (codigo)",
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Item description / Descripcion del item",
    )
    unit_measure: Optional[int] = Field(
        default=None,
        description=(
            "Unit of measure code / Unidad de medida (uniMedida)"
        ),
    )
    quantity: Decimal = Field(
        ...,
        gt=0,
        description="Quantity of items / Cantidad de items",
    )
    unit_price: Decimal = Field(
        ...,
        ge=0,
        description="Price per unit / Precio por unidad",
    )
    original_price: Optional[Decimal] = Field(
        default=None,
        ge=0,
        description=(
            "Original unit price / Precio unitario original (precioUni)"
        ),
    )
    discount: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Discount amount / Descuento (montoDescu)",
    )
    taxable_sale: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Taxable sale amount / Venta gravada (ventaGravada)",
    )
    exempt_sale: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Exempt sale amount / Venta exenta (ventaExenta)",
    )
    non_subject_sale: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description=(
            "Non-subject sale amount / Venta no sujeta (ventaNoSuj)"
        ),
    )
    item_tax: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Tax for this item / IVA del item (ivaItem)",
    )
    total: Decimal = Field(
        ...,
        ge=0,
        description="Total for this item / Total del item",
    )

    @model_validator(mode="after")
    def validate_item_total(self) -> "PurchaseInvoiceItem":
        """
        Validate total ~ quantity * unit_price (warning, not error).
        Valida total ~ cantidad * precio_unitario (warning, no error).
        """
        expected_total = self.quantity * self.unit_price
        tolerance = Decimal("0.01")
        if abs(self.total - expected_total) > tolerance:
            logger.warning(
                "Purchase item total mismatch: expected %s, "
                "got %s for '%s'",
                expected_total,
                self.total,
                self.description,
            )
        return self

    class Config:
        """Pydantic configuration / Configuracion de Pydantic."""

        json_encoders = {Decimal: lambda v: float(v)}


class PurchaseInvoice(BaseModel):
    """
    Complete purchase invoice model / Modelo de factura de compra completa.

    Canonical model that unifies all purchase invoice formats.
    Modelo canonico que unifica todos los formatos de facturas de compra.

    The company is the RECEIVER; the supplier is the ISSUER.
    La empresa es el RECEPTOR; el proveedor es el EMISOR.
    """

    # === DOCUMENT IDENTIFICATION / IDENTIFICACION DEL DOCUMENTO ===
    document_number: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description=(
            "Unique document number / Numero unico de documento"
            " (codigoGeneracion)"
        ),
    )
    control_number: Optional[str] = Field(
        default=None,
        max_length=100,
        description=(
            "Official control number / Numero de control"
            " (numeroControl)"
        ),
    )
    document_type: PurchaseDocumentType = Field(
        default=PurchaseDocumentType.FACTURA,
        description="DTE document type / Tipo de documento DTE",
    )
    issue_date: date = Field(
        ...,
        description="Invoice issue date / Fecha de emision",
    )
    emission_time: Optional[str] = Field(
        default=None,
        max_length=10,
        description="Emission time / Hora de emision (horEmi)",
    )
    currency: str = Field(
        default="USD",
        max_length=5,
        description="Currency code / Moneda (tipoMoneda)",
    )
    dte_version: Optional[int] = Field(
        default=None,
        description="DTE schema version / Version del esquema DTE",
    )

    # === SUPPLIER / PROVEEDOR (quien emite la factura) ===
    supplier: SupplierInfo = Field(
        ...,
        description=(
            "Supplier information / Informacion del proveedor (emisor)"
        ),
    )

    # === RECEIVER / RECEPTOR (la empresa = nosotros) ===
    receiver_name: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Receiver name / Nombre del receptor",
    )
    receiver_nit: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Receiver NIT / NIT del receptor",
    )
    receiver_nrc: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Receiver NRC / NRC del receptor",
    )
    receiver_doc_type: Optional[str] = Field(
        default=None,
        max_length=10,
        description=(
            "Receiver document type / Tipo de documento del receptor"
        ),
    )
    receiver_address: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Receiver address / Direccion del receptor",
    )
    receiver_phone: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Receiver phone / Telefono del receptor",
    )
    receiver_email: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Receiver email / Correo del receptor",
    )

    # === ITEMS / ITEMS (productos/servicios comprados) ===
    items: list[PurchaseInvoiceItem] = Field(
        default_factory=list,
        description="Invoice line items / Items de la factura",
    )

    # === FINANCIAL SUMMARY / RESUMEN FINANCIERO ===
    subtotal: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Subtotal before tax / Subtotal antes de impuestos",
    )
    total_taxable: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Total taxable sales / Total gravado",
    )
    total_exempt: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Total exempt sales / Total exento",
    )
    total_non_subject: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Total non-subject sales / Total no sujeto",
    )
    total_discount: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Total discount / Total descuento",
    )
    tax: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Tax amount / Monto de IVA (totalIva)",
    )
    iva_retained: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="IVA retained / IVA retenido",
    )
    total: Decimal = Field(
        ...,
        ge=0,
        description="Total amount / Monto total (totalPagar)",
    )

    # === EXTRAS ===
    total_in_words: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Total in words / Total en letras (totalLetras)",
    )
    payment_condition: Optional[int] = Field(
        default=None,
        description=(
            "Payment condition: 1=Cash, 2=Credit /"
            " Condicion: 1=Contado, 2=Credito"
        ),
    )
    appendix_data: Optional[dict] = Field(
        default=None,
        description="Appendix data / Datos del apendice",
    )
    tax_seal: Optional[str] = Field(
        default=None,
        max_length=200,
        description=(
            "Tax authority seal / Sello de Hacienda (SelloRecibido)"
        ),
    )

    # === PROCESSING METADATA / METADATOS DEL PROCESAMIENTO ===
    source_file: Optional[str] = Field(
        default=None,
        description="Source file path / Ruta del archivo fuente",
    )
    detected_format: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Detected format / Formato detectado",
    )
    detection_confidence: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
        description="Detection confidence (0-1) / Confianza (0-1)",
    )
    processing_warnings: list[str] = Field(
        default_factory=list,
        description="Processing warnings / Advertencias del procesamiento",
    )
    raw_data: Optional[dict] = Field(
        default=None,
        description=(
            "Original complete JSON / JSON original completo"
            " (cero perdida)"
        ),
    )

    @field_validator("issue_date", mode="before")
    @classmethod
    def parse_date(cls, value: Union[str, date]) -> date:
        """
        Parse date from string if needed.
        Parsea la fecha desde string si es necesario.

        Formats: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY
        """
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
            raise ValueError(f"Invalid date format: {value}")
        raise ValueError(f"Cannot parse date from {type(value)}")

    @model_validator(mode="after")
    def validate_totals(self) -> "PurchaseInvoice":
        """
        Validate total ~ subtotal + tax (warning, not error).
        Valida total ~ subtotal + impuesto (warning, no error).
        """
        expected_total = self.subtotal + self.tax
        tolerance = Decimal("0.01")
        if abs(self.total - expected_total) > tolerance:
            logger.warning(
                "Purchase invoice %s total mismatch: "
                "expected %s (subtotal=%s + tax=%s), got %s",
                self.document_number,
                expected_total,
                self.subtotal,
                self.tax,
                self.total,
            )
        return self

    @model_validator(mode="after")
    def validate_items_subtotal(self) -> "PurchaseInvoice":
        """
        Validate subtotal ~ sum(items.total) (warning, not error).
        Valida subtotal ~ suma(items.total) (warning, no error).
        """
        if self.items:
            items_sum = sum(item.total for item in self.items)
            tolerance = Decimal("0.01")
            if abs(self.subtotal - items_sum) > tolerance:
                logger.warning(
                    "Purchase invoice %s subtotal mismatch: "
                    "items sum=%s, subtotal=%s",
                    self.document_number,
                    items_sum,
                    self.subtotal,
                )
        return self

    class Config:
        """Pydantic configuration / Configuracion de Pydantic."""

        json_encoders = {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat(),
        }
