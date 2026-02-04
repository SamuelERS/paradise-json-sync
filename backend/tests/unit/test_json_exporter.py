"""
JSON Exporter Tests / Tests del Exportador JSON
================================================

Unit tests for the JSON export functionality.
Tests unitarios para la funcionalidad de exportación JSON.
"""

import json
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
    ]


class TestJSONExporter:
    """Tests for JSON export functionality / Tests para exportación JSON."""

    def test_export_creates_file(self, sample_invoices, tmp_path):
        """Test that export creates a file / Verifica que exportar crea un archivo."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test.json"
        result = exporter.export_to_json(sample_invoices, str(output_path))
        assert Path(result).exists()

    def test_export_valid_json(self, sample_invoices, tmp_path):
        """Test that output is valid JSON / Verifica que el resultado sea JSON válido."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test.json"
        exporter.export_to_json(sample_invoices, str(output_path))
        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)
            assert "invoices" in data

    def test_export_contains_all_invoices(self, sample_invoices, tmp_path):
        """Test that all invoices are exported / Verifica que todas las facturas se exporten."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test.json"
        exporter.export_to_json(sample_invoices, str(output_path))
        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)
            assert len(data["invoices"]) == 1

    def test_export_with_metadata(self, sample_invoices, tmp_path):
        """Test export with metadata / Verifica exportación con metadata."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test.json"
        exporter.export_to_json(sample_invoices, str(output_path), include_metadata=True)
        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)
            assert "metadata" in data
            assert "total_invoices" in data["metadata"]

    def test_export_without_metadata(self, sample_invoices, tmp_path):
        """Test export without metadata / Verifica exportación sin metadata."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test.json"
        exporter.export_to_json(sample_invoices, str(output_path), include_metadata=False)
        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)
            assert "metadata" not in data

    def test_export_invoice_structure(self, sample_invoices, tmp_path):
        """Test invoice JSON structure / Verifica estructura JSON de factura."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test.json"
        exporter.export_to_json(sample_invoices, str(output_path))
        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)
            inv = data["invoices"][0]
            assert "document_number" in inv
            assert "customer" in inv
            assert "amounts" in inv
            assert "items" in inv

    def test_export_items_included(self, sample_invoices, tmp_path):
        """Test that items are included / Verifica que los items se incluyen."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test.json"
        exporter.export_to_json(sample_invoices, str(output_path))
        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)
            items = data["invoices"][0]["items"]
            assert len(items) == 1
            assert items[0]["description"] == "Producto A"

    def test_export_adds_extension(self, sample_invoices, tmp_path):
        """Test that extension is added automatically / Verifica extensión automática."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test"
        result = exporter.export_to_json(sample_invoices, str(output_path))
        assert result.endswith(".json")

    def test_export_empty_invoices_raises_error(self, tmp_path):
        """Test that empty list raises error / Verifica error con lista vacía."""
        exporter = ExcelExporter()
        output_path = tmp_path / "test.json"
        with pytest.raises(ExcelExporterError):
            exporter.export_to_json([], str(output_path))
