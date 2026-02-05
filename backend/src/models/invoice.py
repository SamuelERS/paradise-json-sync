"""
Invoice Models / Modelos de Factura
===================================

Pydantic models for invoice data validation and serialization.
Modelos Pydantic para validación y serialización de datos de facturas.

This module defines:
Este módulo define:
- InvoiceType: Enum for invoice types (factura, ccf, nota_credito)
               Enum para tipos de factura
- InvoiceItem: Individual line item in an invoice
               Ítem individual en una factura
- Invoice: Complete invoice with header and items
           Factura completa con encabezado e ítems
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger(__name__)


class InvoiceType(str, Enum):
    """
    Invoice type enumeration / Enumeración de tipos de factura.

    Values / Valores:
    - FACTURA: Standard invoice / Factura estándar
    - CCF: Comprobante de Crédito Fiscal / Tax Credit Certificate
    - NOTA_CREDITO: Credit note / Nota de crédito
    """

    FACTURA = "factura"
    CCF = "ccf"
    NOTA_CREDITO = "nota_credito"


class InvoiceItem(BaseModel):
    """
    Invoice line item / Ítem de línea de factura.

    Represents a single product or service in an invoice.
    Representa un producto o servicio individual en una factura.

    Attributes / Atributos:
        quantity: Number of units / Cantidad de unidades
        description: Item description / Descripción del ítem
        unit_price: Price per unit / Precio por unidad
        total: Total for this item (quantity * unit_price)
               Total del ítem (cantidad * precio_unitario)
        item_number: Item sequence number / Número de secuencia del ítem
        product_code: Product code / Código del producto
        unit_measure: Unit of measure code / Código de unidad de medida
        original_price: Original price before adjustments / Precio original
        discount: Discount amount / Monto de descuento
        item_tax: Tax amount for this item / IVA del ítem
        non_subject_sale: Non-subject sale amount / Venta no sujeta
        exempt_sale: Exempt sale amount / Venta exenta
        taxable_sale: Taxable sale amount / Venta gravada
    """

    quantity: Decimal = Field(
        ...,
        gt=0,
        description="Quantity of items / Cantidad de ítems",
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Item description / Descripción del ítem",
    )
    unit_price: Decimal = Field(
        ...,
        ge=0,
        description="Price per unit / Precio por unidad",
    )
    total: Decimal = Field(
        ...,
        ge=0,
        description="Total for this item / Total del ítem",
    )
    # DTE-specific fields / Campos específicos de DTE
    item_number: Optional[int] = Field(
        default=None,
        description="Item sequence number / Número de ítem (numItem)",
    )
    product_code: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Product code / Código del producto (codigo)",
    )
    unit_measure: Optional[int] = Field(
        default=None,
        description="Unit of measure code / Unidad de medida (uniMedida)",
    )
    original_price: Optional[Decimal] = Field(
        default=None,
        ge=0,
        description="Original unit price / Precio unitario original (precioUni)",
    )
    discount: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Discount amount / Descuento (montoDescu)",
    )
    item_tax: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Tax for this item / IVA del ítem (ivaItem)",
    )
    non_subject_sale: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Non-subject sale amount / Venta no sujeta (ventaNoSuj)",
    )
    exempt_sale: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Exempt sale amount / Venta exenta (ventaExenta)",
    )
    taxable_sale: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Taxable sale amount / Venta gravada (ventaGravada)",
    )

    @model_validator(mode="after")
    def validate_total_calculation(self) -> "InvoiceItem":
        """
        Validate that total equals quantity * unit_price.
        Valida que el total sea igual a cantidad * precio_unitario.
        """
        expected_total = self.quantity * self.unit_price
        tolerance = Decimal("0.01")
        if abs(self.total - expected_total) > tolerance:
            logger.warning(
                "Item total mismatch: expected %s, got %s for '%s'",
                expected_total,
                self.total,
                self.description,
            )
        return self

    class Config:
        """Pydantic configuration / Configuración de Pydantic."""

        json_encoders = {Decimal: lambda v: float(v)}


class Invoice(BaseModel):
    """
    Complete invoice model / Modelo de factura completa.

    Represents a full invoice with header information and line items.
    Representa una factura completa con información de encabezado e ítems.

    Includes full DTE (Documento Tributario Electrónico) support for
    El Salvador electronic invoicing standard.

    Attributes / Atributos:
        document_number: Unique invoice number / Número único de factura
        invoice_type: Type of invoice / Tipo de factura
        issue_date: Date of issuance / Fecha de emisión
        customer_name: Customer name / Nombre del cliente
        customer_id: Customer tax ID / Identificación fiscal del cliente
        items: List of line items / Lista de ítems
        subtotal: Sum of items before tax / Suma de ítems antes de impuestos
        tax: Tax amount / Monto de impuesto
        total: Final total (subtotal + tax) / Total final
        source_file: Original source file path / Ruta del archivo fuente
    """

    # === Core fields / Campos principales ===
    document_number: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique document number / Número único de documento (codigoGeneracion)",
    )
    invoice_type: InvoiceType = Field(
        default=InvoiceType.FACTURA,
        description="Type of invoice / Tipo de factura",
    )
    issue_date: date = Field(
        ...,
        description="Invoice issue date / Fecha de emisión",
    )
    customer_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Customer name / Nombre del cliente",
    )
    customer_id: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Customer tax ID / Identificación fiscal (numDocumento)",
    )
    items: list[InvoiceItem] = Field(
        default_factory=list,
        description="Invoice line items / Ítems de la factura",
    )
    subtotal: Decimal = Field(
        ...,
        ge=0,
        description="Subtotal before tax / Subtotal antes de impuestos",
    )
    tax: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Tax amount / Monto de impuesto (totalIva)",
    )
    total: Decimal = Field(
        ...,
        ge=0,
        description="Total amount / Monto total (totalPagar)",
    )
    source_file: Optional[str] = Field(
        default=None,
        description="Source file path / Ruta del archivo fuente",
    )

    # === DTE Identification / Identificación DTE ===
    control_number: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Official control number / Número de control (numeroControl)",
    )
    emission_time: Optional[str] = Field(
        default=None,
        max_length=10,
        description="Emission time / Hora de emisión (horEmi)",
    )
    currency: str = Field(
        default="USD",
        max_length=5,
        description="Currency code / Moneda (tipoMoneda)",
    )

    # === Issuer data / Datos del emisor ===
    issuer_nit: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Issuer NIT / NIT del emisor",
    )
    issuer_nrc: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Issuer NRC / NRC del emisor",
    )
    issuer_name: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Issuer legal name / Nombre legal del emisor",
    )
    issuer_commercial_name: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Issuer commercial name / Nombre comercial del emisor",
    )
    issuer_address: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Issuer address / Dirección del emisor",
    )

    # === Customer additional data / Datos adicionales del cliente ===
    customer_doc_type: Optional[str] = Field(
        default=None,
        max_length=10,
        description="Customer document type / Tipo de documento del cliente (tipoDocumento)",
    )
    customer_nrc: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Customer NRC / NRC del cliente",
    )
    customer_address: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Customer address / Dirección del cliente",
    )
    customer_phone: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Customer phone / Teléfono del cliente",
    )
    customer_email: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Customer email / Correo del cliente",
    )

    # === Summary fields / Campos de resumen ===
    total_non_subject: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Total non-subject sales / Total no sujeto (totalNoSuj)",
    )
    total_exempt: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Total exempt sales / Total exento (totalExenta)",
    )
    total_taxable: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Total taxable sales / Total gravado (totalGravada)",
    )
    total_discount: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Total discount / Total descuento (totalDescu)",
    )
    total_in_words: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Total amount in words / Total en letras (totalLetras)",
    )
    payment_condition: Optional[int] = Field(
        default=None,
        description="Payment condition: 1=Cash, 2=Credit / Condición: 1=Contado, 2=Crédito (condicionOperacion)",
    )

    # === Appendix data / Datos del apéndice ===
    seller_name: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Seller name / Nombre del vendedor",
    )
    internal_doc_number: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Internal document number / N° de documento interno",
    )

    # === Tax seal / Sello fiscal ===
    tax_seal: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Tax authority seal / Sello de Hacienda (SelloRecibido)",
    )

    @field_validator("issue_date", mode="before")
    @classmethod
    def parse_date(cls, value: Union[str, date]) -> date:
        """
        Parse date from string if needed.
        Parsea la fecha desde string si es necesario.
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
    def validate_totals(self) -> "Invoice":
        """
        Validate that total equals subtotal + tax.
        Valida que el total sea igual a subtotal + impuesto.
        """
        expected_total = self.subtotal + self.tax
        tolerance = Decimal("0.01")
        if abs(self.total - expected_total) > tolerance:
            logger.warning(
                "Invoice %s total mismatch: expected %s (subtotal=%s + tax=%s), got %s",
                self.document_number,
                expected_total,
                self.subtotal,
                self.tax,
                self.total,
            )
        return self

    @model_validator(mode="after")
    def validate_items_subtotal(self) -> "Invoice":
        """
        Validate that subtotal matches sum of item totals.
        Valida que el subtotal coincida con la suma de totales de ítems.
        """
        if self.items:
            items_sum = sum(item.total for item in self.items)
            tolerance = Decimal("0.01")
            if abs(self.subtotal - items_sum) > tolerance:
                logger.warning(
                    "Invoice %s subtotal mismatch: items sum=%s, subtotal=%s",
                    self.document_number,
                    items_sum,
                    self.subtotal,
                )
        return self

    class Config:
        """Pydantic configuration / Configuración de Pydantic."""

        json_encoders = {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat(),
        }


class InvoiceValidationError(Exception):
    """
    Custom exception for invoice validation errors.
    Excepción personalizada para errores de validación de facturas.

    Attributes / Atributos:
        message: Error description / Descripción del error
        field: Field that caused the error / Campo que causó el error
        value: Invalid value / Valor inválido
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[str] = None,
    ) -> None:
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation / Retorna representación en string."""
        if self.field:
            return f"{self.message} (field={self.field}, value={self.value})"
        return self.message
