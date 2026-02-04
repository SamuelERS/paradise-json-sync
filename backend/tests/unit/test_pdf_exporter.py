"""
PDF Exporter Tests / Tests del Exportador PDF
==============================================

Unit tests for the PDF export functionality.
Tests unitarios para la funcionalidad de exportación PDF.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from src.core.excel_exporter import ExcelExporter, ExcelExporterError
from src.models.invoice import Invoice, InvoiceType


@pytest.fixture
def sample_invoices():
    """
    Create sample invoices for testing.
    Crea facturas de ejemplo para testing.
    """
    return [
        Invoice(
            document_number="INV-001",
            invoice_type=InvoiceType.FACTURA,
            issue_date=date(2026, 2, 1),
            customer_name="Cliente Uno",
            customer_id="NIT-001",
            subtotal=Decimal("100.00"),
            tax=Decimal("13.00"),
            total=Decimal("113.00"),
            source_file="factura1.json",
            items=[],
        ),
    ]


class TestPDFExporter:
    """Tests for PDF export functionality / Tests para exportación PDF."""

    def test_export_creates_file(self, sample_invoices, tmp_path):
        """Test that export creates a file / Verifica que exportar crea un archivo."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test.pdf"
        result = exporter.export_to_pdf(sample_invoices, str(output_path))
        assert Path(result).exists()

    def test_export_file_is_pdf(self, sample_invoices, tmp_path):
        """Test that file is a valid PDF / Verifica que el archivo sea PDF válido."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test.pdf"
        exporter.export_to_pdf(sample_invoices, str(output_path))
        with open(output_path, "rb") as f:
            header = f.read(4)
            assert header == b"%PDF"

    def test_export_adds_extension(self, sample_invoices, tmp_path):
        """Test that extension is added automatically / Verifica extensión automática."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test"
        result = exporter.export_to_pdf(sample_invoices, str(output_path))
        assert result.endswith(".pdf")

    def test_export_with_summary(self, sample_invoices, tmp_path):
        """Test export with summary / Verifica exportación con resumen."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test.pdf"
        result = exporter.export_to_pdf(sample_invoices, str(output_path), include_summary=True)
        assert Path(result).exists()

    def test_export_without_summary(self, sample_invoices, tmp_path):
        """Test export without summary / Verifica exportación sin resumen."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test.pdf"
        result = exporter.export_to_pdf(sample_invoices, str(output_path), include_summary=False)
        assert Path(result).exists()

    def test_export_custom_title(self, sample_invoices, tmp_path):
        """Test export with custom title / Verifica exportación con título personalizado."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test.pdf"
        result = exporter.export_to_pdf(sample_invoices, str(output_path), title="Custom Report")
        assert Path(result).exists()

    def test_export_empty_invoices_raises_error(self, tmp_path):
        """Test that empty list raises error / Verifica error con lista vacía."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test.pdf"
        with pytest.raises(ExcelExporterError):
            exporter.export_to_pdf([], str(output_path))
