"""
Data Validator / Validador de Datos
===================================

Validation logic for invoice data integrity.
Lógica de validación para integridad de datos de facturas.

This module provides:
Este módulo provee:
- validate_invoice: Validate a single invoice
                    Valida una factura individual
- validate_totals: Verify invoice total calculations
                   Verifica cálculos de totales
- validate_date_range: Check date consistency across invoices
                       Verifica consistencia de fechas
"""

import logging
from datetime import date, timedelta
from decimal import Decimal

from src.models.invoice import Invoice

logger = logging.getLogger(__name__)


class DataValidator:
    """
    Invoice data validator / Validador de datos de facturas.

    Provides comprehensive validation for invoice data integrity.
    Provee validación completa para integridad de datos de facturas.

    Attributes / Atributos:
        tolerance: Decimal tolerance for comparisons
                   Tolerancia decimal para comparaciones
        max_date_range_days: Maximum days between oldest and newest invoice
                             Máximo de días entre factura más antigua y más nueva
    """

    def __init__(
        self,
        tolerance: Decimal = Decimal("0.01"),
        max_date_range_days: int = 365,
    ) -> None:
        """
        Initialize the validator.
        Inicializa el validador.

        Args / Argumentos:
            tolerance: Decimal tolerance for total comparisons
                       Tolerancia decimal para comparación de totales
            max_date_range_days: Maximum allowed date range in days
                                 Rango máximo permitido de fechas en días
        """
        self.tolerance = tolerance
        self.max_date_range_days = max_date_range_days
        logger.debug(
            "DataValidator initialized with tolerance=%s, max_date_range=%d days",
            tolerance,
            max_date_range_days,
        )

    def validate_invoice(
        self,
        invoice: Invoice,
    ) -> tuple[bool, list[str]]:
        """
        Validate a single invoice for data integrity.
        Valida una factura individual para integridad de datos.

        Args / Argumentos:
            invoice: Invoice to validate / Factura a validar

        Returns / Retorna:
            Tuple of (is_valid, list of error messages)
            Tupla de (es_válido, lista de mensajes de error)
        """
        errors: list[str] = []

        # Validate document number / Validar número de documento
        if not invoice.document_number or not invoice.document_number.strip():
            errors.append("Document number is required / Número de documento requerido")

        # Validate customer name / Validar nombre de cliente
        if not invoice.customer_name or not invoice.customer_name.strip():
            errors.append("Customer name is required / Nombre de cliente requerido")

        # Validate issue date / Validar fecha de emisión
        if not self._validate_issue_date(invoice.issue_date):
            errors.append(f"Invalid issue date: {invoice.issue_date} / Fecha de emisión inválida")

        # Validate totals / Validar totales
        total_errors = self._validate_total_calculations(invoice)
        errors.extend(total_errors)

        # Validate items if present / Validar ítems si existen
        if invoice.items:
            item_errors = self._validate_items(invoice)
            errors.extend(item_errors)

        is_valid = len(errors) == 0

        if not is_valid:
            logger.warning(
                "Invoice %s validation failed with %d errors",
                invoice.document_number,
                len(errors),
            )
        else:
            logger.debug("Invoice %s passed validation", invoice.document_number)

        return is_valid, errors

    def validate_totals(self, invoice: Invoice) -> bool:
        """
        Validate that invoice totals are mathematically correct.
        Valida que los totales de factura sean matemáticamente correctos.

        Args / Argumentos:
            invoice: Invoice to validate / Factura a validar

        Returns / Retorna:
            True if totals are valid / True si los totales son válidos
        """
        errors = self._validate_total_calculations(invoice)
        return len(errors) == 0

    def validate_date_range(
        self,
        invoices: list[Invoice],
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> bool:
        """
        Validate that all invoices fall within acceptable date range.
        Valida que todas las facturas estén dentro del rango de fechas aceptable.

        Args / Argumentos:
            invoices: List of invoices to validate / Lista de facturas a validar
            start_date: Optional start date filter / Filtro de fecha inicial opcional
            end_date: Optional end date filter / Filtro de fecha final opcional

        Returns / Retorna:
            True if all dates are valid / True si todas las fechas son válidas
        """
        if not invoices:
            logger.debug("No invoices to validate date range")
            return True

        dates = [inv.issue_date for inv in invoices]
        min_date = min(dates)
        max_date = max(dates)

        # Check internal range / Verificar rango interno
        date_span = (max_date - min_date).days
        if date_span > self.max_date_range_days:
            logger.warning(
                "Date range exceeds maximum: %d days (max=%d)",
                date_span,
                self.max_date_range_days,
            )
            return False

        # Check against provided boundaries / Verificar contra límites provistos
        if start_date and min_date < start_date:
            logger.warning(
                "Invoice date %s is before start date %s",
                min_date,
                start_date,
            )
            return False

        if end_date and max_date > end_date:
            logger.warning(
                "Invoice date %s is after end date %s",
                max_date,
                end_date,
            )
            return False

        logger.debug(
            "Date range validation passed: %s to %s (%d days)",
            min_date,
            max_date,
            date_span,
        )
        return True

    def _validate_issue_date(self, issue_date: date) -> bool:
        """
        Validate that issue date is reasonable.
        Valida que la fecha de emisión sea razonable.
        """
        today = date.today()
        min_date = today - timedelta(days=self.max_date_range_days * 2)
        max_date = today + timedelta(days=30)  # Allow some future dates

        if issue_date < min_date:
            logger.warning("Issue date %s is too old", issue_date)
            return False

        if issue_date > max_date:
            logger.warning("Issue date %s is too far in the future", issue_date)
            return False

        return True

    def _validate_total_calculations(self, invoice: Invoice) -> list[str]:
        """
        Validate mathematical correctness of totals.
        Valida corrección matemática de totales.
        """
        errors: list[str] = []

        # Validate total = subtotal + tax
        expected_total = invoice.subtotal + invoice.tax
        if abs(invoice.total - expected_total) > self.tolerance:
            errors.append(
                f"Total mismatch: {invoice.total} != {invoice.subtotal} + {invoice.tax} / "
                f"Total incorrecto"
            )

        # Validate subtotal against items sum
        if invoice.items:
            items_sum = sum(item.total for item in invoice.items)
            if abs(invoice.subtotal - items_sum) > self.tolerance:
                errors.append(
                    f"Subtotal mismatch: {invoice.subtotal} != sum of items {items_sum} / "
                    f"Subtotal incorrecto"
                )

        # Validate non-negative values
        if invoice.subtotal < 0:
            errors.append("Subtotal cannot be negative / Subtotal no puede ser negativo")

        if invoice.tax < 0:
            errors.append("Tax cannot be negative / Impuesto no puede ser negativo")

        if invoice.total < 0:
            errors.append("Total cannot be negative / Total no puede ser negativo")

        return errors

    def _validate_items(self, invoice: Invoice) -> list[str]:
        """
        Validate invoice line items.
        Valida ítems de línea de factura.
        """
        errors: list[str] = []

        for i, item in enumerate(invoice.items):
            # Validate item total calculation
            expected_item_total = item.quantity * item.unit_price
            if abs(item.total - expected_item_total) > self.tolerance:
                errors.append(
                    f"Item {i + 1} total mismatch: {item.total} != "
                    f"{item.quantity} * {item.unit_price} / "
                    f"Total de ítem {i + 1} incorrecto"
                )

            # Validate description
            if not item.description or not item.description.strip():
                errors.append(f"Item {i + 1} missing description / Ítem {i + 1} sin descripción")

        return errors

    def validate_batch(
        self,
        invoices: list[Invoice],
    ) -> tuple[list[Invoice], list[tuple[Invoice, list[str]]]]:
        """
        Validate a batch of invoices, separating valid from invalid.
        Valida un lote de facturas, separando válidas de inválidas.

        Args / Argumentos:
            invoices: List of invoices to validate / Lista de facturas a validar

        Returns / Retorna:
            Tuple of (valid_invoices, list of (invalid_invoice, errors))
            Tupla de (facturas_válidas, lista de (factura_inválida, errores))
        """
        valid_invoices: list[Invoice] = []
        invalid_invoices: list[tuple[Invoice, list[str]]] = []

        for invoice in invoices:
            is_valid, errors = self.validate_invoice(invoice)
            if is_valid:
                valid_invoices.append(invoice)
            else:
                invalid_invoices.append((invoice, errors))

        logger.info(
            "Batch validation: %d valid, %d invalid out of %d total",
            len(valid_invoices),
            len(invalid_invoices),
            len(invoices),
        )

        return valid_invoices, invalid_invoices
