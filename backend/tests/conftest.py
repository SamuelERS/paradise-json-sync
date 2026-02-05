"""
Test Fixtures / Fixtures de Prueba
==================================

Shared fixtures for unit tests.
Fixtures compartidos para pruebas unitarias.

This module provides:
Este módulo provee:
- sample_json_data: Sample JSON invoice data
                    Datos JSON de factura de muestra
- sample_json_file: Temporary JSON file with sample data
                    Archivo JSON temporal con datos de muestra
- sample_pdf_file: Temporary PDF file for testing
                   Archivo PDF temporal para pruebas
- sample_invoice: Sample Invoice object
                  Objeto Invoice de muestra
- multiple_invoices: List of sample invoices
                     Lista de facturas de muestra
"""

import json
import sys
from collections.abc import Generator
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.models.invoice import Invoice, InvoiceItem, InvoiceType


@pytest.fixture
def sample_json_data() -> dict:
    """
    Sample JSON data for an invoice.
    Datos JSON de muestra para una factura.
    """
    return {
        "document_number": "FAC-001",
        "invoice_type": "factura",
        "issue_date": "2025-02-04",
        "customer_name": "Test Customer / Cliente de Prueba",
        "customer_id": "1234567-8",
        "items": [
            {
                "quantity": 2,
                "description": "Product A / Producto A",
                "unit_price": 10.00,
                "total": 20.00,
            },
            {
                "quantity": 1,
                "description": "Product B / Producto B",
                "unit_price": 15.50,
                "total": 15.50,
            },
        ],
        "subtotal": 35.50,
        "tax": 4.62,
        "total": 40.12,
    }


@pytest.fixture
def sample_json_data_minimal() -> dict:
    """
    Minimal valid JSON data for an invoice (required fields only).
    Datos JSON mínimos válidos para una factura (solo campos requeridos).
    """
    return {
        "document_number": "FAC-002",
        "issue_date": "2025-02-04",
        "customer_name": "Minimal Customer",
        "subtotal": 100.00,
        "total": 100.00,
    }


@pytest.fixture
def sample_json_data_invalid() -> dict:
    """
    Invalid JSON data (missing required fields).
    Datos JSON inválidos (faltan campos requeridos).
    """
    return {
        "invoice_type": "factura",
        "customer_name": "Test Customer",
        # Missing: document_number, issue_date, total
    }


@pytest.fixture
def sample_json_file(
    sample_json_data: dict,
    tmp_path: Path,
) -> Generator[Path, None, None]:
    """
    Temporary JSON file with sample data.
    Archivo JSON temporal con datos de muestra.
    """
    json_file = tmp_path / "test_invoice.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(sample_json_data, f, indent=2)

    yield json_file


@pytest.fixture
def sample_json_files(
    sample_json_data: dict,
    tmp_path: Path,
) -> Generator[list[Path], None, None]:
    """
    Multiple temporary JSON files for batch testing.
    Múltiples archivos JSON temporales para pruebas por lote.
    """
    files = []
    for i in range(3):
        data = sample_json_data.copy()
        data["document_number"] = f"FAC-{i + 1:03d}"
        data["total"] = 40.12 + i * 10

        json_file = tmp_path / f"test_invoice_{i + 1}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        files.append(json_file)

    yield files


@pytest.fixture
def sample_pdf_file(tmp_path: Path) -> Generator[Path, None, None]:
    """
    Temporary PDF file for testing.
    Archivo PDF temporal para pruebas.

    Creates a minimal valid PDF structure.
    Crea una estructura PDF mínima válida.
    """
    try:
        import fitz

        pdf_file = tmp_path / "test_document.pdf"
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Test PDF Document / Documento PDF de Prueba")
        doc.save(str(pdf_file))
        doc.close()

        yield pdf_file
    except ImportError:
        # Create a minimal PDF manually if PyMuPDF not available
        pdf_file = tmp_path / "test_document.pdf"
        minimal_pdf = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >> endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer << /Size 4 /Root 1 0 R >>
startxref
196
%%EOF"""
        with open(pdf_file, "wb") as f:
            f.write(minimal_pdf)

        yield pdf_file


@pytest.fixture
def sample_pdf_files(tmp_path: Path) -> Generator[list[Path], None, None]:
    """
    Multiple temporary PDF files for merge testing.
    Múltiples archivos PDF temporales para pruebas de unión.
    """
    try:
        import fitz

        files = []
        for i in range(3):
            pdf_file = tmp_path / f"test_document_{i + 1}.pdf"
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((72, 72), f"Test Page {i + 1} / Página de Prueba {i + 1}")
            doc.save(str(pdf_file))
            doc.close()
            files.append(pdf_file)

        yield files
    except ImportError:
        # Skip if PyMuPDF not available
        yield []


@pytest.fixture
def sample_invoice_item() -> InvoiceItem:
    """
    Sample invoice item.
    Ítem de factura de muestra.
    """
    return InvoiceItem(
        quantity=Decimal("2"),
        description="Test Product / Producto de Prueba",
        unit_price=Decimal("25.00"),
        total=Decimal("50.00"),
    )


@pytest.fixture
def sample_invoice(sample_invoice_item: InvoiceItem) -> Invoice:
    """
    Sample complete invoice.
    Factura completa de muestra.
    """
    return Invoice(
        document_number="FAC-001",
        invoice_type=InvoiceType.FACTURA,
        issue_date=date(2025, 2, 4),
        customer_name="Test Customer / Cliente de Prueba",
        customer_id="1234567-8",
        items=[sample_invoice_item],
        subtotal=Decimal("50.00"),
        tax=Decimal("6.50"),
        total=Decimal("56.50"),
        source_file="/path/to/test.json",
    )


@pytest.fixture
def multiple_invoices() -> list[Invoice]:
    """
    List of sample invoices for batch testing.
    Lista de facturas de muestra para pruebas por lote.
    """
    invoices = []

    # Invoice 1: Standard factura
    invoices.append(
        Invoice(
            document_number="FAC-001",
            invoice_type=InvoiceType.FACTURA,
            issue_date=date(2025, 2, 1),
            customer_name="Customer One / Cliente Uno",
            customer_id="1111111-1",
            items=[
                InvoiceItem(
                    quantity=Decimal("1"),
                    description="Item 1",
                    unit_price=Decimal("100.00"),
                    total=Decimal("100.00"),
                ),
            ],
            subtotal=Decimal("100.00"),
            tax=Decimal("13.00"),
            total=Decimal("113.00"),
        )
    )

    # Invoice 2: CCF
    invoices.append(
        Invoice(
            document_number="CCF-001",
            invoice_type=InvoiceType.CCF,
            issue_date=date(2025, 2, 2),
            customer_name="Customer Two / Cliente Dos",
            customer_id="2222222-2",
            items=[
                InvoiceItem(
                    quantity=Decimal("5"),
                    description="Item 2",
                    unit_price=Decimal("20.00"),
                    total=Decimal("100.00"),
                ),
            ],
            subtotal=Decimal("100.00"),
            tax=Decimal("13.00"),
            total=Decimal("113.00"),
        )
    )

    # Invoice 3: Credit note
    invoices.append(
        Invoice(
            document_number="NC-001",
            invoice_type=InvoiceType.NOTA_CREDITO,
            issue_date=date(2025, 2, 3),
            customer_name="Customer Three / Cliente Tres",
            customer_id="3333333-3",
            items=[
                InvoiceItem(
                    quantity=Decimal("1"),
                    description="Return Item",
                    unit_price=Decimal("50.00"),
                    total=Decimal("50.00"),
                ),
            ],
            subtotal=Decimal("50.00"),
            tax=Decimal("6.50"),
            total=Decimal("56.50"),
        )
    )

    return invoices


@pytest.fixture
def invoice_with_invalid_totals() -> Invoice:
    """
    Invoice with mismatched totals for validation testing.
    Factura con totales incorrectos para pruebas de validación.
    """
    return Invoice(
        document_number="FAC-INVALID",
        invoice_type=InvoiceType.FACTURA,
        issue_date=date(2025, 2, 4),
        customer_name="Invalid Customer",
        items=[
            InvoiceItem(
                quantity=Decimal("1"),
                description="Test Item",
                unit_price=Decimal("100.00"),
                total=Decimal("100.00"),
            ),
        ],
        subtotal=Decimal("100.00"),
        tax=Decimal("13.00"),
        total=Decimal("150.00"),  # Incorrect: should be 113.00
    )


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """
    Temporary directory for output files.
    Directorio temporal para archivos de salida.
    """
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


@pytest.fixture
def corrupted_pdf_file(tmp_path: Path) -> Path:
    """
    Corrupted/invalid PDF file for error handling tests.
    Archivo PDF corrupto/inválido para pruebas de manejo de errores.
    """
    pdf_file = tmp_path / "corrupted.pdf"
    with open(pdf_file, "wb") as f:
        f.write(b"This is not a valid PDF file content")

    return pdf_file


@pytest.fixture
def empty_json_file(tmp_path: Path) -> Path:
    """
    Empty JSON file for error handling tests.
    Archivo JSON vacío para pruebas de manejo de errores.
    """
    json_file = tmp_path / "empty.json"
    with open(json_file, "w", encoding="utf-8") as f:
        f.write("{}")

    return json_file
