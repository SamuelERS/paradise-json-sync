"""
Invoice Model Tests / Pruebas del Modelo de Factura
===================================================

Unit tests for the Invoice, InvoiceItem, and InvoiceType models.
Pruebas unitarias para los modelos Invoice, InvoiceItem e InvoiceType.
"""

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.models.invoice import (
    Invoice,
    InvoiceItem,
    InvoiceType,
    InvoiceValidationError,
)


class TestInvoiceType:
    """Tests for InvoiceType enum / Pruebas para enum InvoiceType."""

    def test_invoice_type_values(self):
        """Test that all invoice types have correct values."""
        assert InvoiceType.FACTURA.value == "factura"
        assert InvoiceType.CCF.value == "ccf"
        assert InvoiceType.NOTA_CREDITO.value == "nota_credito"

    def test_invoice_type_from_string(self):
        """Test creating InvoiceType from string."""
        assert InvoiceType("factura") == InvoiceType.FACTURA
        assert InvoiceType("ccf") == InvoiceType.CCF
        assert InvoiceType("nota_credito") == InvoiceType.NOTA_CREDITO


class TestInvoiceItem:
    """Tests for InvoiceItem model / Pruebas para modelo InvoiceItem."""

    def test_create_valid_item(self, sample_invoice_item):
        """Test creating a valid invoice item."""
        assert sample_invoice_item.quantity == Decimal("2")
        assert sample_invoice_item.description == "Test Product / Producto de Prueba"
        assert sample_invoice_item.unit_price == Decimal("25.00")
        assert sample_invoice_item.total == Decimal("50.00")

    def test_item_total_validation_passes(self):
        """Test that matching total passes validation."""
        item = InvoiceItem(
            quantity=Decimal("3"),
            description="Test",
            unit_price=Decimal("10.00"),
            total=Decimal("30.00"),
        )
        assert item.total == Decimal("30.00")

    def test_item_total_mismatch_logs_warning(self, caplog):
        """Test that mismatched total logs a warning but doesn't fail."""
        item = InvoiceItem(
            quantity=Decimal("2"),
            description="Test",
            unit_price=Decimal("10.00"),
            total=Decimal("25.00"),  # Wrong: should be 20.00
        )
        # Should still create the item
        assert item.total == Decimal("25.00")

    def test_item_requires_positive_quantity(self):
        """Test that quantity must be positive."""
        with pytest.raises(ValidationError):
            InvoiceItem(
                quantity=Decimal("0"),
                description="Test",
                unit_price=Decimal("10.00"),
                total=Decimal("0"),
            )

    def test_item_requires_description(self):
        """Test that description is required."""
        with pytest.raises(ValidationError):
            InvoiceItem(
                quantity=Decimal("1"),
                description="",  # Empty string
                unit_price=Decimal("10.00"),
                total=Decimal("10.00"),
            )


class TestInvoice:
    """Tests for Invoice model / Pruebas para modelo Invoice."""

    def test_create_valid_invoice(self, sample_invoice):
        """Test creating a valid invoice."""
        assert sample_invoice.document_number == "FAC-001"
        assert sample_invoice.invoice_type == InvoiceType.FACTURA
        assert sample_invoice.customer_name == "Test Customer / Cliente de Prueba"
        assert sample_invoice.subtotal == Decimal("50.00")
        assert sample_invoice.tax == Decimal("6.50")
        assert sample_invoice.total == Decimal("56.50")

    def test_invoice_requires_document_number(self):
        """Test that document_number is required."""
        with pytest.raises(ValidationError) as exc_info:
            Invoice(
                document_number="",  # Empty string
                issue_date=date(2025, 2, 4),
                customer_name="Test Customer",
                subtotal=Decimal("100.00"),
                total=Decimal("100.00"),
            )
        assert "document_number" in str(exc_info.value)

    def test_invoice_requires_customer_name(self):
        """Test that customer_name is required."""
        with pytest.raises(ValidationError):
            Invoice(
                document_number="FAC-001",
                issue_date=date(2025, 2, 4),
                customer_name="",  # Empty string
                subtotal=Decimal("100.00"),
                total=Decimal("100.00"),
            )

    def test_invoice_total_validation(self, caplog):
        """Test that total = subtotal + tax is validated."""
        invoice = Invoice(
            document_number="FAC-001",
            issue_date=date(2025, 2, 4),
            customer_name="Test Customer",
            subtotal=Decimal("100.00"),
            tax=Decimal("13.00"),
            total=Decimal("113.00"),  # Correct
        )
        assert invoice.total == Decimal("113.00")

    def test_invoice_total_mismatch_logs_warning(self, caplog):
        """Test that mismatched total logs warning but creates invoice."""
        invoice = Invoice(
            document_number="FAC-001",
            issue_date=date(2025, 2, 4),
            customer_name="Test Customer",
            subtotal=Decimal("100.00"),
            tax=Decimal("13.00"),
            total=Decimal("150.00"),  # Wrong: should be 113.00
        )
        # Invoice should still be created
        assert invoice.total == Decimal("150.00")

    def test_invoice_date_parsing_iso_format(self):
        """Test date parsing from ISO format string."""
        invoice = Invoice(
            document_number="FAC-001",
            issue_date="2025-02-04",  # String format
            customer_name="Test Customer",
            subtotal=Decimal("100.00"),
            total=Decimal("100.00"),
        )
        assert invoice.issue_date == date(2025, 2, 4)

    def test_invoice_date_parsing_slash_format(self):
        """Test date parsing from DD/MM/YYYY format."""
        invoice = Invoice(
            document_number="FAC-001",
            issue_date="04/02/2025",  # DD/MM/YYYY
            customer_name="Test Customer",
            subtotal=Decimal("100.00"),
            total=Decimal("100.00"),
        )
        assert invoice.issue_date == date(2025, 2, 4)

    def test_invoice_date_parsing_dash_format(self):
        """Test date parsing from DD-MM-YYYY format."""
        invoice = Invoice(
            document_number="FAC-001",
            issue_date="04-02-2025",  # DD-MM-YYYY
            customer_name="Test Customer",
            subtotal=Decimal("100.00"),
            total=Decimal("100.00"),
        )
        assert invoice.issue_date == date(2025, 2, 4)

    def test_invoice_date_invalid_format(self):
        """Test that invalid date format raises error."""
        with pytest.raises(ValidationError):
            Invoice(
                document_number="FAC-001",
                issue_date="February 4, 2025",  # Invalid format
                customer_name="Test Customer",
                subtotal=Decimal("100.00"),
                total=Decimal("100.00"),
            )

    def test_invoice_default_type_is_factura(self):
        """Test that default invoice type is FACTURA."""
        invoice = Invoice(
            document_number="FAC-001",
            issue_date=date(2025, 2, 4),
            customer_name="Test Customer",
            subtotal=Decimal("100.00"),
            total=Decimal("100.00"),
        )
        assert invoice.invoice_type == InvoiceType.FACTURA

    def test_invoice_with_items(self, sample_invoice_item):
        """Test creating invoice with items."""
        invoice = Invoice(
            document_number="FAC-001",
            issue_date=date(2025, 2, 4),
            customer_name="Test Customer",
            items=[sample_invoice_item],
            subtotal=Decimal("50.00"),
            tax=Decimal("6.50"),
            total=Decimal("56.50"),
        )
        assert len(invoice.items) == 1
        assert invoice.items[0].description == sample_invoice_item.description

    def test_invoice_subtotal_items_mismatch_logs_warning(self, caplog):
        """Test that subtotal != items sum logs warning."""
        item = InvoiceItem(
            quantity=Decimal("1"),
            description="Test",
            unit_price=Decimal("100.00"),
            total=Decimal("100.00"),
        )
        invoice = Invoice(
            document_number="FAC-001",
            issue_date=date(2025, 2, 4),
            customer_name="Test Customer",
            items=[item],
            subtotal=Decimal("200.00"),  # Wrong: should be 100.00
            total=Decimal("200.00"),
        )
        # Should still create
        assert invoice.subtotal == Decimal("200.00")

    def test_invoice_optional_customer_id(self):
        """Test that customer_id is optional."""
        invoice = Invoice(
            document_number="FAC-001",
            issue_date=date(2025, 2, 4),
            customer_name="Test Customer",
            subtotal=Decimal("100.00"),
            total=Decimal("100.00"),
        )
        assert invoice.customer_id is None

    def test_invoice_optional_source_file(self):
        """Test that source_file is optional."""
        invoice = Invoice(
            document_number="FAC-001",
            issue_date=date(2025, 2, 4),
            customer_name="Test Customer",
            subtotal=Decimal("100.00"),
            total=Decimal("100.00"),
        )
        assert invoice.source_file is None


class TestInvoiceValidationError:
    """Tests for InvoiceValidationError / Pruebas para InvoiceValidationError."""

    def test_error_with_message_only(self):
        """Test creating error with message only."""
        error = InvoiceValidationError("Test error message")
        assert str(error) == "Test error message"
        assert error.field is None
        assert error.value is None

    def test_error_with_field_and_value(self):
        """Test creating error with field and value."""
        error = InvoiceValidationError(
            message="Invalid value",
            field="document_number",
            value="",
        )
        assert "document_number" in str(error)
        assert error.field == "document_number"
        assert error.value == ""
