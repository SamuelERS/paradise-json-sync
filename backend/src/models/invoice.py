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

    document_number: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique document number / Número único de documento",
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
        description="Customer tax ID / Identificación fiscal",
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
        description="Tax amount / Monto de impuesto",
    )
    total: Decimal = Field(
        ...,
        ge=0,
        description="Total amount / Monto total",
    )
    source_file: Optional[str] = Field(
        default=None,
        description="Source file path / Ruta del archivo fuente",
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
