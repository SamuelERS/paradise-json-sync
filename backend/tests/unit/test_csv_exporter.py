"""
CSV Exporter Tests / Tests del Exportador CSV
==============================================

Unit tests for the CSV export functionality.
Tests unitarios para la funcionalidad de exportación CSV.
"""

import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from src.core.excel_exporter import ExcelExporter, ExcelExporterError
from src.models.invoice import Invoice, InvoiceItem, InvoiceType


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
            items=[
                InvoiceItem(
                    description="Producto A",
                    quantity=Decimal("2"),
                    unit_price=Decimal("50.00"),
                    total=Decimal("100.00"),
                )
            ],
        ),
        Invoice(
            document_number="INV-002",
            invoice_type=InvoiceType.CCF,
            issue_date=date(2026, 2, 2),
            customer_name="Cliente Dos",
            customer_id="NIT-002",
            subtotal=Decimal("200.00"),
            tax=Decimal("26.00"),
            total=Decimal("226.00"),
            source_file="factura2.json",
            items=[],
        ),
    ]


class TestCSVExporter:
    """Tests for CSV export functionality / Tests para exportación CSV."""

    def test_export_creates_file(self, sample_invoices, tmp_path):
        """Test that export creates a file / Verifica que exportar crea un archivo."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test.csv"
        result = exporter.export_to_csv(sample_invoices, str(output_path))
        assert Path(result).exists()

    def test_export_contains_headers(self, sample_invoices, tmp_path):
        """Test that export includes headers / Verifica que incluye encabezados."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test.csv"
        exporter.export_to_csv(sample_invoices, str(output_path))
        with open(output_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
            assert any("Document Number" in h for h in headers)

    def test_export_contains_all_invoices(self, sample_invoices, tmp_path):
        """Test that all invoices are exported / Verifica que todas las facturas se exporten."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test.csv"
        exporter.export_to_csv(sample_invoices, str(output_path))
        with open(output_path, encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 3  # header + 2 invoices

    def test_export_without_header(self, sample_invoices, tmp_path):
        """Test export without header / Verifica exportación sin encabezado."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test.csv"
        exporter.export_to_csv(sample_invoices, str(output_path), include_header=False)
        with open(output_path, encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 2  # no header

    def test_export_custom_delimiter(self, sample_invoices, tmp_path):
        """Test export with custom delimiter / Verifica exportación con delimitador personalizado."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test.csv"
        exporter.export_to_csv(sample_invoices, str(output_path), delimiter=";")
        with open(output_path, encoding="utf-8") as f:
            content = f.read()
            assert ";" in content

    def test_export_adds_extension(self, sample_invoices, tmp_path):
        """Test that extension is added automatically / Verifica extensión automática."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test"
        result = exporter.export_to_csv(sample_invoices, str(output_path))
        assert result.endswith(".csv")

    def test_export_empty_invoices_raises_error(self, tmp_path):
        """Test that empty list raises error / Verifica error con lista vacía."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test.csv"
        with pytest.raises(ExcelExporterError):
            exporter.export_to_csv([], str(output_path))
