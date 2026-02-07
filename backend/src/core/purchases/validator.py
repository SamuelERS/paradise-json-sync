"""
Purchase Validator / Validador de Compras
==========================================

Validates normalized purchase invoice data for completeness and consistency.
Valida datos normalizados de facturas de compra para completitud y consistencia.

This module provides / Este modulo provee:
- ValidationLevel: Enum for issue severity (ERROR, WARNING, INFO)
- ValidationIssue: Model for a single validation problem
- ValidationResult: Complete validation result for one invoice
- PurchaseValidator: Main validator class with all rules
"""

import logging
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from src.models.purchase_invoice import PurchaseInvoice

logger = logging.getLogger(__name__)


class ValidationLevel(str, Enum):
    """
    Validation severity levels / Niveles de severidad de validacion.

    ERROR: Invoice rejected / Factura rechazada
    WARNING: Invoice accepted with warning / Aceptada con advertencia
    INFO: Informational only / Solo informativo
    """

    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class ValidationIssue(BaseModel):
    """
    A single validation problem / Un problema de validacion.

    Attributes / Atributos:
        level: Severity level / Nivel de severidad
        field: Field with the problem / Campo con el problema
        message: Description / Descripcion del problema
        expected: Expected value / Valor esperado
        actual: Found value / Valor encontrado
        duplicate_of: Duplicate source file / Archivo duplicado
    """

    level: ValidationLevel
    field: str
    message: str
    expected: Optional[str] = None
    actual: Optional[str] = None
    duplicate_of: Optional[str] = None

    def __str__(self) -> str:
        """String representation / Representacion en texto."""
        return f"[{self.level.value}] {self.field}: {self.message}"


class ValidationResult(BaseModel):
    """
    Complete validation result / Resultado completo de validacion.

    Attributes / Atributos:
        is_valid: True if no ERRORs / True si no hay ERRORs
        issues: All problems found / Todos los problemas encontrados
        error_count: Number of errors / Cantidad de errores
        warning_count: Number of warnings / Cantidad de warnings
        info_count: Number of infos / Cantidad de infos
    """

    is_valid: bool
    issues: list[ValidationIssue]
    error_count: int
    warning_count: int
    info_count: int

    @property
    def has_errors(self) -> bool:
        """Check if has errors / Verifica si tiene errores."""
        return self.error_count > 0

    @property
    def has_warnings(self) -> bool:
        """Check if has warnings / Verifica si tiene warnings."""
        return self.warning_count > 0


# Required fields: missing = ERROR
REQUIRED_FIELDS = {
    "document_number": "Numero de documento",
    "issue_date": "Fecha de emision",
    "total": "Total",
    "supplier.name": "Nombre del proveedor",
}

# Recommended fields: missing = WARNING
RECOMMENDED_FIELDS = {
    "control_number": "Numero de control",
    "supplier.nit": "NIT del proveedor",
    "items": "Items de la factura (lista)",
    "subtotal": "Subtotal",
    "tax": "IVA",
}


class PurchaseValidator:
    """
    Purchase invoice validator / Validador de facturas de compra.

    Executes all validations and returns a complete result.
    Ejecuta todas las validaciones y retorna un resultado completo.
    """

    def __init__(
        self, tolerance: Decimal = Decimal("0.02")
    ) -> None:
        """
        Initialize validator with tolerance.
        Inicializa validador con tolerancia.

        Args / Argumentos:
            tolerance: Numeric tolerance for comparisons
        """
        self.tolerance = tolerance

    def validate(
        self,
        invoice: PurchaseInvoice,
        existing: Optional[list[PurchaseInvoice]] = None,
    ) -> ValidationResult:
        """
        Execute all validations on an invoice.
        Ejecuta todas las validaciones sobre una factura.

        Args / Argumentos:
            invoice: Invoice to validate / Factura a validar
            existing: Already processed invoices / Facturas ya procesadas

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

        errors = [
            i for i in issues if i.level == ValidationLevel.ERROR
        ]
        warnings = [
            i for i in issues if i.level == ValidationLevel.WARNING
        ]
        infos = [
            i for i in issues if i.level == ValidationLevel.INFO
        ]

        return ValidationResult(
            is_valid=len(errors) == 0,
            issues=issues,
            error_count=len(errors),
            warning_count=len(warnings),
            info_count=len(infos),
        )

    def validate_required_fields(
        self, invoice: PurchaseInvoice
    ) -> list[ValidationIssue]:
        """
        Check required and recommended fields.
        Verifica campos requeridos y recomendados.
        """
        issues: list[ValidationIssue] = []

        for field_path, label in REQUIRED_FIELDS.items():
            value = self._get_nested(invoice, field_path)
            if value is None or (isinstance(value, str) and not value):
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    field=field_path,
                    message=f"Campo requerido faltante: {label}",
                ))

        for field_path, label in RECOMMENDED_FIELDS.items():
            value = self._get_nested(invoice, field_path)
            if value is None or (isinstance(value, str) and not value):
                if field_path == "items" and value is not None:
                    if len(value) == 0:
                        issues.append(ValidationIssue(
                            level=ValidationLevel.WARNING,
                            field=field_path,
                            message=f"Campo recomendado vacio: {label}",
                        ))
                else:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        field=field_path,
                        message=f"Campo recomendado faltante: {label}",
                    ))

        return issues

    def validate_totals(
        self, invoice: PurchaseInvoice
    ) -> list[ValidationIssue]:
        """
        Verify mathematical consistency of totals.
        Verifica consistencia matematica de totales.
        """
        issues: list[ValidationIssue] = []

        # Total ~ Subtotal + IVA
        if invoice.subtotal > 0 or invoice.tax > 0:
            expected_total = invoice.subtotal + invoice.tax
            if abs(invoice.total - expected_total) > self.tolerance:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    field="total",
                    message=(
                        f"Total ({invoice.total}) != "
                        f"Subtotal ({invoice.subtotal}) + "
                        f"IVA ({invoice.tax})"
                    ),
                    expected=str(expected_total),
                    actual=str(invoice.total),
                ))

        # Subtotal ~ sum(items)
        if invoice.items:
            items_sum = sum(item.total for item in invoice.items)
            if abs(invoice.subtotal - items_sum) > self.tolerance:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    field="subtotal",
                    message=(
                        f"Subtotal ({invoice.subtotal}) != "
                        f"Suma items ({items_sum})"
                    ),
                ))

        # IVA ~ 13% of taxable base
        if invoice.total_taxable > 0 and invoice.tax > 0:
            expected_iva = invoice.total_taxable * Decimal("0.13")
            if abs(invoice.tax - expected_iva) > Decimal("0.10"):
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    field="tax",
                    message=(
                        f"IVA ({invoice.tax}) != "
                        f"13% de gravado ({expected_iva})"
                    ),
                ))

        # Categories sum ~ Subtotal
        category_sum = (
            invoice.total_taxable
            + invoice.total_exempt
            + invoice.total_non_subject
        )
        if category_sum > 0:
            if abs(invoice.subtotal - category_sum) > self.tolerance:
                issues.append(ValidationIssue(
                    level=ValidationLevel.INFO,
                    field="categories",
                    message=(
                        f"Categorias ({category_sum}) != "
                        f"Subtotal ({invoice.subtotal})"
                    ),
                ))

        return issues

    def validate_dates(
        self, invoice: PurchaseInvoice
    ) -> list[ValidationIssue]:
        """
        Verify date coherence.
        Verifica coherencia de fechas.
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
        Detect if invoice already exists in the batch.
        Detecta si la factura ya existe en el lote.
        """
        for existing_inv in existing:
            if (
                invoice.control_number
                and invoice.control_number == existing_inv.control_number
                and invoice.supplier.nit
                and invoice.supplier.nit == existing_inv.supplier.nit
            ):
                return ValidationIssue(
                    level=ValidationLevel.ERROR,
                    field="control_number",
                    message=(
                        f"Factura duplicada: {invoice.control_number} "
                        f"del proveedor {invoice.supplier.name}"
                    ),
                    duplicate_of=existing_inv.source_file,
                )

        for existing_inv in existing:
            if invoice.document_number == existing_inv.document_number:
                return ValidationIssue(
                    level=ValidationLevel.WARNING,
                    field="document_number",
                    message=(
                        f"Posible duplicado por document_number: "
                        f"{invoice.document_number}"
                    ),
                    duplicate_of=existing_inv.source_file,
                )

        return None

    def validate_batch(
        self, invoices: list[PurchaseInvoice]
    ) -> dict:
        """
        Validate a complete batch of invoices.
        Valida un lote completo de facturas.

        Returns / Retorna:
            Dict with valid, invalid, counts
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

    @staticmethod
    def _get_nested(
        obj: PurchaseInvoice, field_path: str
    ) -> object:
        """
        Get nested field value using dot notation.
        Obtiene valor de campo anidado usando notacion punto.
        """
        parts = field_path.split(".")
        current: object = obj
        for part in parts:
            if current is None:
                return None
            current = getattr(current, part, None)
        return current
