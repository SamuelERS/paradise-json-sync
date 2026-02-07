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

# IMPORTANT: Set TESTING environment variable BEFORE any other imports
# IMPORTANTE: Configurar variable TESTING ANTES de cualquier otro import
# This disables rate limiting in the application
# Esto deshabilita el rate limiting en la aplicación
import os
os.environ["TESTING"] = "true"


def pytest_configure(config):
    """
    Pytest hook that runs before test collection.
    Hook de pytest que se ejecuta antes de la recolección de tests.

    Ensures TESTING is set before any test modules are imported.
    """
    os.environ["TESTING"] = "true"


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
from src.models.purchase_invoice import (
    PurchaseDocumentType,
    PurchaseInvoice,
    PurchaseInvoiceItem,
    SupplierInfo,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Test environment cleanup fixture.
    Fixture de limpieza del entorno de pruebas.

    TESTING env var is set at module level (above) to ensure it's
    available before any test modules import src.main.
    This fixture handles cleanup after all tests complete.
    """
    yield
    os.environ.pop("TESTING", None)


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
    Archivo JSON vacio para pruebas de manejo de errores.
    """
    json_file = tmp_path / "empty.json"
    with open(json_file, "w", encoding="utf-8") as f:
        f.write("{}")

    return json_file


# === Purchase Invoice Fixtures / Fixtures de Facturas de Compra ===


@pytest.fixture
def sample_supplier_info() -> SupplierInfo:
    """
    Sample supplier information.
    Informacion de proveedor de muestra.
    """
    return SupplierInfo(
        name="DISTRIBUIDORA ABC S.A. DE C.V.",
        commercial_name="ABC Distribuciones",
        nit="0614-123456-789-0",
        nrc="12345-6",
        economic_activity="Venta al por mayor",
        address="Blvd. Los Heroes, San Salvador",
        phone="2222-3333",
        email="ventas@abc.com.sv",
        establishment_code="S001",
        establishment_type="Sucursal",
    )


@pytest.fixture
def sample_purchase_invoice_item() -> PurchaseInvoiceItem:
    """
    Sample purchase invoice item.
    Item de factura de compra de muestra.
    """
    return PurchaseInvoiceItem(
        item_number=1,
        product_code="PAP-001",
        description="Papel Bond Carta Resma 500 hojas",
        unit_measure=59,
        quantity=Decimal("10"),
        unit_price=Decimal("3.50"),
        taxable_sale=Decimal("35.00"),
        item_tax=Decimal("4.55"),
        total=Decimal("35.00"),
    )


@pytest.fixture
def sample_purchase_invoice(
    sample_supplier_info: SupplierInfo,
    sample_purchase_invoice_item: PurchaseInvoiceItem,
) -> PurchaseInvoice:
    """
    Sample complete purchase invoice.
    Factura de compra completa de muestra.
    """
    return PurchaseInvoice(
        document_number="A1B2C3D4-E5F6-7890-ABCD-EF1234567890",
        control_number="DTE-03-00000001-000000000000001",
        document_type=PurchaseDocumentType.CCF,
        issue_date=date(2026, 2, 6),
        emission_time="14:30:00",
        currency="USD",
        dte_version=3,
        supplier=sample_supplier_info,
        receiver_name="MI EMPRESA S.A. DE C.V.",
        receiver_nit="0614-999999-999-9",
        items=[sample_purchase_invoice_item],
        subtotal=Decimal("35.00"),
        total_taxable=Decimal("35.00"),
        tax=Decimal("4.55"),
        total=Decimal("39.55"),
        total_in_words="TREINTA Y NUEVE 55/100 DOLARES",
        payment_condition=1,
        source_file="factura_abc_001.json",
        detected_format="DTE_STANDARD",
        detection_confidence=0.95,
        raw_data={"identificacion": {}, "emisor": {}, "receptor": {}},
    )


# === Format Detector Fixtures / Fixtures del Detector de Formato ===


@pytest.fixture
def sample_dte_standard_json() -> dict:
    """
    Sample DTE_STANDARD JSON (Hacienda official format).
    JSON DTE_STANDARD de muestra (formato oficial Hacienda).
    """
    return {
        "identificacion": {
            "version": 3,
            "ambiente": "01",
            "tipoDte": "03",
            "numeroControl": "DTE-03-00000001-000000000000001",
            "codigoGeneracion": "A1B2C3D4-E5F6-7890-ABCD-EF1234567890",
            "tipoModelo": 1,
            "tipoOperacion": 1,
            "fecEmi": "2026-02-06",
            "horEmi": "14:30:00",
            "tipoMoneda": "USD",
        },
        "emisor": {
            "nit": "0614-123456-789-0",
            "nrc": "12345-6",
            "nombre": "DISTRIBUIDORA ABC S.A. DE C.V.",
        },
        "receptor": {
            "nit": "0614-999999-999-9",
            "nombre": "MI EMPRESA S.A. DE C.V.",
        },
        "cuerpoDocumento": [
            {"numItem": 1, "descripcion": "Papel Bond", "ventaGravada": 35.00}
        ],
        "resumen": {
            "totalGravada": 35.00,
            "totalIva": 4.55,
            "totalPagar": 39.55,
        },
        "apendice": [{"campo": "valor"}],
    }


@pytest.fixture
def sample_dte_variant_a_json() -> dict:
    """
    Sample DTE_VARIANT_A JSON (items in 'detalle' key).
    JSON DTE_VARIANT_A de muestra (items en clave 'detalle').
    """
    return {
        "identificacion": {
            "codigoGeneracion": "B2C3D4E5-F6A7-8901-BCDE-F12345678901",
            "tipoDte": "01",
            "fecEmi": "2026-02-06",
        },
        "emisor": {"nombre": "PROVEEDOR XYZ"},
        "receptor": {"nombre": "MI EMPRESA"},
        "detalle": [
            {"numItem": 1, "descripcion": "Producto A", "total": 100.00}
        ],
        "totales": {"totalAPagar": 113.00},
    }


@pytest.fixture
def sample_dte_variant_b_json() -> dict:
    """
    Sample DTE_VARIANT_B JSON (flattened summary at root).
    JSON DTE_VARIANT_B de muestra (resumen aplanado en raiz).
    """
    return {
        "identificacion": {
            "version": 3,
            "tipoDte": "03",
            "codigoGeneracion": "C3D4E5F6-A7B8-9012-CDEF-123456789012",
            "fecEmi": "2026-02-06",
        },
        "emisor": {"nombre": "PROVEEDOR 123"},
        "cuerpoDocumento": [
            {"numItem": 1, "descripcion": "Servicio B", "total": 100.00}
        ],
        "totalGravada": 100.00,
        "totalIva": 13.00,
        "totalPagar": 113.00,
    }


@pytest.fixture
def sample_generic_flat_json() -> dict:
    """
    Sample GENERIC_FLAT JSON (no DTE structure, common field names).
    JSON GENERIC_FLAT de muestra (sin estructura DTE, nombres comunes).
    """
    return {
        "numero_factura": "F-001",
        "fecha": "2026-02-06",
        "proveedor": "ABC S.A.",
        "nit_proveedor": "0614-123456-789-0",
        "items": [
            {"descripcion": "Producto X", "cantidad": 2, "total": 20.00}
        ],
        "total": 113.00,
    }


@pytest.fixture
def sample_unknown_json() -> dict:
    """
    Sample unrecognizable JSON (no matching fingerprint).
    JSON irreconocible de muestra (sin fingerprint coincidente).
    """
    return {
        "foo": "bar",
        "baz": 123,
        "nested": {"x": 1, "y": 2},
    }
