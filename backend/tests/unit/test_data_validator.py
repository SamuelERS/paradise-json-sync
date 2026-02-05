"""
DataValidator Tests / Pruebas del Validador de Datos
====================================================

Unit tests for the DataValidator class.
Pruebas unitarias para la clase DataValidator.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.core.data_validator import DataValidator
from src.models.invoice import Invoice, InvoiceItem


class TestDataValidatorInit:
    """Tests for DataValidator initialization."""

    def test_default_initialization(self):
        """Test default initialization values."""
        validator = DataValidator()
        assert validator.tolerance == Decimal("0.01")
        assert validator.max_date_range_days == 365

    def test_custom_initialization(self):
        """Test custom initialization values."""
        validator = DataValidator(
            tolerance=Decimal("0.001"),
            max_date_range_days=30,
        )
        assert validator.tolerance == Decimal("0.001")
        assert validator.max_date_range_days == 30


class TestValidateInvoice:
    """Tests for validate_invoice method."""

    def test_valid_invoice_passes(self, sample_invoice):
        """Test that a valid invoice passes validation."""
        validator = DataValidator()
        is_valid, errors = validator.validate_invoice(sample_invoice)

        assert is_valid is True
        assert len(errors) == 0

    def test_invoice_without_document_number_fails(self):
        """Test that invoice without document_number fails."""
        validator = DataValidator()

        # Create invoice with whitespace-only document number
        invoice = Invoice(
            document_number="   ",
            issue_date=date(2025, 2, 4),
            customer_name="Test Customer",
            subtotal=Decimal("100.00"),
            total=Decimal("100.00"),
        )

        is_valid, errors = validator.validate_invoice(invoice)

        assert is_valid is False
        assert any("document" in e.lower() for e in errors)

    def test_invoice_without_customer_name_fails(self):
        """Test that invoice without customer_name fails."""
        validator = DataValidator()

        invoice = Invoice(
            document_number="FAC-001",
            issue_date=date(2025, 2, 4),
            customer_name="   ",  # Whitespace only
            subtotal=Decimal("100.00"),
            total=Decimal("100.00"),
        )

        is_valid, errors = validator.validate_invoice(invoice)

        assert is_valid is False
        assert any("customer" in e.lower() for e in errors)

    def test_invoice_with_incorrect_totals_fails(self, invoice_with_invalid_totals):
        """Test that invoice with incorrect totals fails."""
        validator = DataValidator()
        is_valid, errors = validator.validate_invoice(invoice_with_invalid_totals)

        assert is_valid is False
        assert any("total" in e.lower() for e in errors)

    def test_invoice_with_future_date_fails(self):
        """Test that invoice with far future date fails."""
        validator = DataValidator()

        future_date = date.today() + timedelta(days=60)
        invoice = Invoice(
            document_number="FAC-001",
            issue_date=future_date,
            customer_name="Test Customer",
            subtotal=Decimal("100.00"),
            total=Decimal("100.00"),
        )

        is_valid, errors = validator.validate_invoice(invoice)

        assert is_valid is False
        assert any("date" in e.lower() for e in errors)

    def test_invoice_with_valid_recent_future_date_passes(self):
        """Test that invoice with near future date passes."""
        validator = DataValidator()

        # 10 days in future should be OK
        near_future = date.today() + timedelta(days=10)
        invoice = Invoice(
            document_number="FAC-001",
            issue_date=near_future,
            customer_name="Test Customer",
            subtotal=Decimal("100.00"),
            total=Decimal("100.00"),
        )

        is_valid, errors = validator.validate_invoice(invoice)

        assert is_valid is True


class TestValidateTotals:
    """Tests for validate_totals method."""

    def test_correct_totals_pass(self, sample_invoice):
        """Test that correct totals pass validation."""
        validator = DataValidator()
        assert validator.validate_totals(sample_invoice) is True

    def test_incorrect_totals_fail(self, invoice_with_invalid_totals):
        """Test that incorrect totals fail validation."""
        validator = DataValidator()
        assert validator.validate_totals(invoice_with_invalid_totals) is False

    def test_totals_within_tolerance_pass(self):
        """Test that totals within tolerance pass."""
        validator = DataValidator(tolerance=Decimal("0.01"))

        invoice = Invoice(
            document_number="FAC-001",
            issue_date=date(2025, 2, 4),
            customer_name="Test Customer",
            subtotal=Decimal("100.00"),
            tax=Decimal("13.00"),
            total=Decimal("113.005"),  # Within 0.01 tolerance
        )

        assert validator.validate_totals(invoice) is True

    def test_negative_subtotal_rejected_by_pydantic(self):
        """Test that negative subtotal is rejected at Pydantic level."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Invoice(
                document_number="FAC-001",
                issue_date=date(2025, 2, 4),
                customer_name="Test Customer",
                subtotal=Decimal("-100.00"),
                total=Decimal("-100.00"),
            )


class TestValidateDateRange:
    """Tests for validate_date_range method."""

    def test_empty_list_passes(self):
        """Test that empty invoice list passes."""
        validator = DataValidator()
        assert validator.validate_date_range([]) is True

    def test_single_invoice_passes(self, sample_invoice):
        """Test that single invoice passes."""
        validator = DataValidator()
        assert validator.validate_date_range([sample_invoice]) is True

    def test_invoices_within_range_pass(self, multiple_invoices):
        """Test that invoices within date range pass."""
        validator = DataValidator(max_date_range_days=365)
        assert validator.validate_date_range(multiple_invoices) is True

    def test_invoices_exceeding_range_fail(self):
        """Test that invoices exceeding date range fail."""
        validator = DataValidator(max_date_range_days=30)

        invoices = [
            Invoice(
                document_number="FAC-001",
                issue_date=date(2025, 1, 1),
                customer_name="Test",
                subtotal=Decimal("100.00"),
                total=Decimal("100.00"),
            ),
            Invoice(
                document_number="FAC-002",
                issue_date=date(2025, 6, 1),  # 151 days later
                customer_name="Test",
                subtotal=Decimal("100.00"),
                total=Decimal("100.00"),
            ),
        ]

        assert validator.validate_date_range(invoices) is False

    def test_date_range_with_start_boundary(self, multiple_invoices):
        """Test date range with start date boundary."""
        validator = DataValidator()

        # All invoices are in February 2025
        start_date = date(2025, 2, 1)
        assert validator.validate_date_range(multiple_invoices, start_date=start_date) is True

        # Set start date after all invoices
        late_start = date(2025, 3, 1)
        assert validator.validate_date_range(multiple_invoices, start_date=late_start) is False

    def test_date_range_with_end_boundary(self, multiple_invoices):
        """Test date range with end date boundary."""
        validator = DataValidator()

        # All invoices are in February 2025
        end_date = date(2025, 2, 28)
        assert validator.validate_date_range(multiple_invoices, end_date=end_date) is True

        # Set end date before all invoices
        early_end = date(2025, 1, 31)
        assert validator.validate_date_range(multiple_invoices, end_date=early_end) is False


class TestValidateBatch:
    """Tests for validate_batch method."""

    def test_all_valid_invoices(self, multiple_invoices):
        """Test batch with all valid invoices."""
        validator = DataValidator()
        valid, invalid = validator.validate_batch(multiple_invoices)

        assert len(valid) == 3
        assert len(invalid) == 0

    def test_mixed_valid_invalid_invoices(self, multiple_invoices, invoice_with_invalid_totals):
        """Test batch with mixed valid and invalid invoices."""
        validator = DataValidator()

        all_invoices = multiple_invoices + [invoice_with_invalid_totals]
        valid, invalid = validator.validate_batch(all_invoices)

        assert len(valid) == 3
        assert len(invalid) == 1
        assert invalid[0][0].document_number == "FAC-INVALID"

    def test_empty_batch(self):
        """Test empty batch."""
        validator = DataValidator()
        valid, invalid = validator.validate_batch([])

        assert len(valid) == 0
        assert len(invalid) == 0


class TestValidateItems:
    """Tests for item validation."""

    def test_valid_items_pass(self, sample_invoice):
        """Test that valid items pass validation."""
        validator = DataValidator()
        is_valid, errors = validator.validate_invoice(sample_invoice)

        assert is_valid is True

    def test_item_with_wrong_total_fails(self):
        """Test that item with wrong total fails."""
        validator = DataValidator()

        item = InvoiceItem(
            quantity=Decimal("2"),
            description="Test Item",
            unit_price=Decimal("10.00"),
            total=Decimal("50.00"),  # Wrong: should be 20.00
        )

        invoice = Invoice(
            document_number="FAC-001",
            issue_date=date(2025, 2, 4),
            customer_name="Test Customer",
            items=[item],
            subtotal=Decimal("50.00"),
            total=Decimal("50.00"),
        )

        is_valid, errors = validator.validate_invoice(invoice)

        assert is_valid is False
        assert any("item" in e.lower() for e in errors)
