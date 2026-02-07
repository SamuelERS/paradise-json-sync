"""
Purchase Validator / Validador de Compras
==========================================

Validates normalized purchase invoices for data quality and integrity.
Valida facturas de compra normalizadas para calidad e integridad de datos.

This module provides / Este modulo provee:
- ValidationLevel: Severity enum (ERROR, WARNING, INFO)
                   Enum de severidad (ERROR, WARNING, INFO)
- ValidationIssue: Individual validation problem model
                   Modelo de problema de validacion individual
- ValidationResult: Complete validation result model
                    Modelo de resultado de validacion completo
- PurchaseValidator: Main validator with all validation rules
                     Validador principal con todas las reglas
"""

import logging
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel

from src.models.purchase_invoice import PurchaseInvoice

logger = logging.getLogger(__name__)


# === Campos requeridos y recomendados / Required and recommended fields ===

REQUIRED_FIELDS: dict[str, str] = {
    "document_number": "Numero de documento",
    "issue_date": "Fecha de emision",
    "total": "Total",
    "supplier.name": "Nombre del proveedor",
}

RECOMMENDED_FIELDS: dict[str, str] = {
    "control_number": "Numero de control",
    "supplier.nit": "NIT del proveedor",
    "items": "Items de la factura (lista)",
    "subtotal": "Subtotal",
    "tax": "IVA",
}

# IVA rate for El Salvador / Tasa de IVA para El Salvador
IVA_RATE = Decimal("0.13")
IVA_TOLERANCE = Decimal("0.10")


class ValidationLevel(str, Enum):
    """
    Validation severity levels / Niveles de severidad de validacion.

    ERROR: Invoice rejected / Factura rechazada
    WARNING: Invoice accepted with warning / Factura aceptada con advertencia
    INFO: Informational only / Solo informativo
    """

    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class ValidationIssue(BaseModel):
    """
    A single validation problem found during inspection.
    Un problema de validacion encontrado durante la inspeccion.
    """

    level: ValidationLevel
    field: str
    message: str
    expected: Optional[str] = None
    actual: Optional[str] = None
    duplicate_of: Optional[str] = None


class ValidationResult(BaseModel):
    """
    Complete validation result for a purchase invoice.
    Resultado completo de validacion para una factura de compra.
    """

    is_valid: bool
    issues: list[ValidationIssue]
    error_count: int
    warning_count: int
    info_count: int

    @property
    def has_errors(self) -> bool:
        """True if there are ERROR-level issues / True si hay issues ERROR."""
        return self.error_count > 0

    @property
    def has_warnings(self) -> bool:
        """True if there are WARNING-level issues / True si hay WARNING."""
        return self.warning_count > 0


def _get_field(obj: Any, field_path: str) -> Any:
    """
    Access a nested field using dot notation.
    Accede a un campo anidado usando notacion de punto.

    Args / Argumentos:
        obj: Object to traverse / Objeto a recorrer
        field_path: Dot-separated path / Ruta separada por puntos

    Returns / Retorna:
        Field value or None / Valor del campo o None
    """
    parts = field_path.split(".")
    current = obj
    for part in parts:
        current = getattr(current, part, None)
        if current is None:
            return None
    return current


class PurchaseValidator:
    """
    Validador de facturas de compra normalizadas.
    Validator for normalized purchase invoices.

    Runs all validations and returns a complete result.
    Ejecuta todas las validaciones y retorna un resultado completo.
    Invoices with ERRORS are rejected; with WARNINGS are accepted.
    Facturas con ERRORES se rechazan; con WARNINGS se aceptan.
    """

    def __init__(
        self,
        tolerance: Decimal = Decimal("0.02"),
    ) -> None:
        self.tolerance = tolerance

    def validate(
        self,
        invoice: PurchaseInvoice,
        existing: Optional[list[PurchaseInvoice]] = None,
    ) -> ValidationResult:
        """
        Run all validations on a purchase invoice.
        Ejecuta todas las validaciones sobre una factura.

        Args / Argumentos:
            invoice: Invoice to validate / Factura a validar
            existing: Previously processed invoices / Facturas ya procesadas

        Returns / Retorna:
            ValidationResult with all issues found
        """
        issues: list[ValidationIssue] = []

        issues.extend(self.validate_required_fields(invoice))
        issues.extend(self.validate_totals(invoice))
        issues.extend(self.validate_dates(invoice))

        if existing:
            dup = self.check_duplicates(invoice, existing)
            if dup:
                issues.append(dup)

        errors = [i for i in issues if i.level == ValidationLevel.ERROR]
        warnings = [
            i for i in issues if i.level == ValidationLevel.WARNING
        ]
        infos = [i for i in issues if i.level == ValidationLevel.INFO]

        return ValidationResult(
            is_valid=len(errors) == 0,
            issues=issues,
            error_count=len(errors),
            warning_count=len(warnings),
            info_count=len(infos),
        )

    def validate_batch(
        self,
        invoices: list[PurchaseInvoice],
    ) -> dict:
        """
        Validate a complete batch of invoices.
        Valida un lote completo de facturas.

        Args / Argumentos:
            invoices: List of invoices / Lista de facturas

        Returns / Retorna:
            Dict with valid, invalid, total, counts
        """
        valid: list[PurchaseInvoice] = []
        invalid: list[tuple[PurchaseInvoice, ValidationResult]] = []
        warning_count = 0

        for invoice in invoices:
            result = self.validate(invoice, existing=valid)
            if result.is_valid:
                valid.append(invoice)
                if result.has_warnings:
                    warning_count += 1
            else:
                invalid.append((invoice, result))

        return {
            "valid": valid,
            "invalid": invalid,
            "total": len(invoices),
            "valid_count": len(valid),
            "invalid_count": len(invalid),
            "warning_count": warning_count,
        }

    def validate_required_fields(
        self,
        invoice: PurchaseInvoice,
    ) -> list[ValidationIssue]:
        """
        Validate required and recommended fields exist.
        Valida que campos requeridos y recomendados existan.

        Args / Argumentos:
            invoice: Invoice to check / Factura a verificar

        Returns / Retorna:
            List of issues found / Lista de problemas encontrados
        """
        issues: list[ValidationIssue] = []

        for field_path, label in REQUIRED_FIELDS.items():
            value = _get_field(invoice, field_path)
            if value is None or value == "":
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    field=field_path,
                    message=f"Campo requerido faltante: {label}",
                ))

        for field_path, label in RECOMMENDED_FIELDS.items():
            value = _get_field(invoice, field_path)
            if field_path == "items":
                if not value:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        field=field_path,
                        message=(
                            f"Campo recomendado faltante: {label}"
                        ),
                    ))
            elif field_path == "subtotal" or field_path == "tax":
                if value is None or value == Decimal("0"):
                    issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        field=field_path,
                        message=(
                            f"Campo recomendado faltante: {label}"
                        ),
                    ))
            elif value is None or value == "":
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    field=field_path,
                    message=(
                        f"Campo recomendado faltante: {label}"
                    ),
                ))

        return issues

    def validate_totals(
        self,
        invoice: PurchaseInvoice,
    ) -> list[ValidationIssue]:
        """
        Validate mathematical consistency of totals.
        Valida consistencia matematica de totales.

        Args / Argumentos:
            invoice: Invoice to check / Factura a verificar

        Returns / Retorna:
            List of issues found / Lista de problemas encontrados
        """
        issues: list[ValidationIssue] = []

        # 1. Total ~ Subtotal + IVA
        if invoice.subtotal > 0 and invoice.tax >= 0:
            expected_total = invoice.subtotal + invoice.tax
            if abs(invoice.total - expected_total) > self.tolerance:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    field="total",
                    message=(
                        f"Total ({invoice.total}) != "
                        f"Subtotal ({invoice.subtotal}) "
                        f"+ IVA ({invoice.tax})"
                    ),
                    expected=str(expected_total),
                    actual=str(invoice.total),
                ))

        # 2. Subtotal ~ Suma de items
        if invoice.items:
            items_sum = sum(
                item.total for item in invoice.items
            )
            if abs(invoice.subtotal - items_sum) > self.tolerance:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    field="subtotal",
                    message=(
                        f"Subtotal ({invoice.subtotal}) != "
                        f"Suma items ({items_sum})"
                    ),
                    expected=str(items_sum),
                    actual=str(invoice.subtotal),
                ))

        # 3. IVA ~ 13% de base gravable (El Salvador)
        if invoice.total_taxable > 0 and invoice.tax > 0:
            expected_iva = invoice.total_taxable * IVA_RATE
            if abs(invoice.tax - expected_iva) > IVA_TOLERANCE:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    field="tax",
                    message=(
                        f"IVA ({invoice.tax}) != "
                        f"13% de gravado ({expected_iva})"
                    ),
                    expected=str(expected_iva),
                    actual=str(invoice.tax),
                ))

        # 4. Gravado + Exento + No Sujeto ~ Subtotal
        category_sum = (
            invoice.total_taxable
            + invoice.total_exempt
            + invoice.total_non_subject
        )
        if category_sum > 0:
            diff = abs(invoice.subtotal - category_sum)
            if diff > self.tolerance:
                issues.append(ValidationIssue(
                    level=ValidationLevel.INFO,
                    field="categories",
                    message=(
                        f"Categorias ({category_sum}) != "
                        f"Subtotal ({invoice.subtotal})"
                    ),
                    expected=str(invoice.subtotal),
                    actual=str(category_sum),
                ))

        return issues

    def validate_dates(
        self,
        invoice: PurchaseInvoice,
    ) -> list[ValidationIssue]:
        """
        Validate date coherence.
        Valida coherencia de fechas.

        Args / Argumentos:
            invoice: Invoice to check / Factura a verificar

        Returns / Retorna:
            List of issues found / Lista de problemas encontrados
        """
        issues: list[ValidationIssue] = []
        today = date.today()

        if invoice.issue_date > today:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                field="issue_date",
                message=f"Fecha futura: {invoice.issue_date}",
            ))

        cutoff = today.replace(year=today.year - 2)
        if invoice.issue_date < cutoff:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                field="issue_date",
                message=(
                    f"Fecha muy antigua: {invoice.issue_date} "
                    f"(mas de 2 anios)"
                ),
            ))

        return issues

    def check_duplicates(
        self,
        invoice: PurchaseInvoice,
        existing: list[PurchaseInvoice],
    ) -> Optional[ValidationIssue]:
        """
        Detect duplicate invoices in the batch.
        Detecta facturas duplicadas en el lote.

        Args / Argumentos:
            invoice: Invoice to check / Factura a verificar
            existing: Previously validated invoices / Facturas ya validadas

        Returns / Retorna:
            ValidationIssue if duplicate found, None otherwise
        """
        # Criterio 1: control_number + NIT -> ERROR
        for existing_inv in existing:
            if (
                invoice.control_number
                and invoice.control_number
                == existing_inv.control_number
                and invoice.supplier.nit
                and invoice.supplier.nit == existing_inv.supplier.nit
            ):
                return ValidationIssue(
                    level=ValidationLevel.ERROR,
                    field="control_number",
                    message=(
                        f"Factura duplicada: "
                        f"{invoice.control_number} "
                        f"del proveedor {invoice.supplier.name}"
                    ),
                    duplicate_of=existing_inv.source_file,
                )

        # Criterio 2: document_number -> WARNING
        for existing_inv in existing:
            if (
                invoice.document_number
                == existing_inv.document_number
            ):
                return ValidationIssue(
                    level=ValidationLevel.WARNING,
                    field="document_number",
                    message=(
                        f"Posible duplicado por "
                        f"document_number: "
                        f"{invoice.document_number}"
                    ),
                    duplicate_of=existing_inv.source_file,
                )

        return None
