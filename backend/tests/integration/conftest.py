"""
Integration Test Fixtures / Fixtures de Tests de Integración

Shared fixtures for backend integration tests.
Fixtures compartidos para tests de integración del backend.
"""

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator, Dict, Any
from io import BytesIO

import pytest
from fastapi.testclient import TestClient

# Import the FastAPI app when it's available
# Importar la app FastAPI cuando esté disponible
# from app.main import app


# ===========================================================================
# Test Configuration / Configuración de Tests
# ===========================================================================

TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEMP_UPLOAD_DIR = Path(tempfile.gettempdir()) / "paradise_test_uploads"


# ===========================================================================
# Sample Test Data / Datos de Prueba de Ejemplo
# ===========================================================================

SAMPLE_INVOICE_JSON = {
    "factura": {
        "numero": "FAC-2024-TEST001",
        "fecha": "2024-01-15",
        "fechaVencimiento": "2024-02-15",
        "tipoComprobante": "factura",
        "moneda": "USD"
    },
    "emisor": {
        "razonSocial": "Test Company S.A.",
        "ruc": "20123456789",
        "direccion": "Test Address 123",
        "telefono": "+51 1 234 5678",
        "email": "test@company.com"
    },
    "receptor": {
        "razonSocial": "Client Test S.R.L.",
        "ruc": "20987654321",
        "direccion": "Client Address 456",
        "telefono": "+51 1 876 5432",
        "email": "client@test.com"
    },
    "items": [
        {
            "codigo": "TEST-001",
            "descripcion": "Test Service",
            "cantidad": 1,
            "unidadMedida": "unidad",
            "precioUnitario": 100.00,
            "subtotal": 100.00,
            "descuento": 0,
            "igv": 18.00,
            "total": 118.00
        }
    ],
    "totales": {
        "subtotal": 100.00,
        "descuentoTotal": 0.00,
        "baseImponible": 100.00,
        "igv": 18.00,
        "total": 118.00
    },
    "observaciones": "Test invoice",
    "metodoPago": "transferencia_bancaria",
    "cuentaBancaria": "123-456789-0-01"
}

SAMPLE_INVOICE_2_JSON = {
    "factura": {
        "numero": "FAC-2024-TEST002",
        "fecha": "2024-01-20",
        "fechaVencimiento": "2024-02-20",
        "tipoComprobante": "factura",
        "moneda": "PEN"
    },
    "emisor": {
        "razonSocial": "Another Company E.I.R.L.",
        "ruc": "20111222333",
        "direccion": "Another Address 789",
        "telefono": "+51 54 123 456",
        "email": "another@company.com"
    },
    "receptor": {
        "razonSocial": "Client Two SAC",
        "ruc": "20444555666",
        "direccion": "Client Two Address 321",
        "telefono": "+51 54 654 321",
        "email": "clienttwo@test.com"
    },
    "items": [
        {
            "codigo": "PROD-100",
            "descripcion": "Product Test",
            "cantidad": 5,
            "unidadMedida": "unidad",
            "precioUnitario": 50.00,
            "subtotal": 250.00,
            "descuento": 25.00,
            "igv": 40.50,
            "total": 265.50
        }
    ],
    "totales": {
        "subtotal": 250.00,
        "descuentoTotal": 25.00,
        "baseImponible": 225.00,
        "igv": 40.50,
        "total": 265.50
    },
    "observaciones": "Second test invoice",
    "metodoPago": "efectivo",
    "cuentaBancaria": None
}

INVALID_JSON = {
    "invalid": "This is not a valid invoice",
    "missing": "required fields"
}


# ===========================================================================
# Fixtures / Fixtures
# ===========================================================================

@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """
    Create test data directory if it doesn't exist.
    Crear directorio de datos de prueba si no existe.
    """
    TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    return TEST_DATA_DIR


@pytest.fixture(scope="function")
def temp_upload_dir() -> Generator[Path, None, None]:
    """
    Create temporary directory for uploads, cleaned after each test.
    Crear directorio temporal para uploads, limpiado después de cada test.
    """
    TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    yield TEMP_UPLOAD_DIR

    # Cleanup after test / Limpiar después del test
    if TEMP_UPLOAD_DIR.exists():
        shutil.rmtree(TEMP_UPLOAD_DIR)


@pytest.fixture(scope="session")
def test_client():
    """
    FastAPI TestClient for API testing.
    TestClient de FastAPI para testing de API.

    Note: Uncomment the import and app reference when main.py is implemented.
    Nota: Descomentar el import y referencia a app cuando main.py esté implementado.
    """
    # When app is ready:
    # Cuando la app esté lista:
    # with TestClient(app) as client:
    #     yield client

    # Placeholder until app is implemented
    # Placeholder hasta que la app esté implementada
    pytest.skip("FastAPI app not yet implemented")


@pytest.fixture
def sample_json_file(temp_upload_dir: Path) -> Path:
    """
    Create a sample JSON invoice file.
    Crear un archivo JSON de factura de ejemplo.
    """
    file_path = temp_upload_dir / "sample-invoice.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(SAMPLE_INVOICE_JSON, f, ensure_ascii=False, indent=2)
    return file_path


@pytest.fixture
def sample_json_file_2(temp_upload_dir: Path) -> Path:
    """
    Create a second sample JSON invoice file.
    Crear un segundo archivo JSON de factura de ejemplo.
    """
    file_path = temp_upload_dir / "sample-invoice-2.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(SAMPLE_INVOICE_2_JSON, f, ensure_ascii=False, indent=2)
    return file_path


@pytest.fixture
def invalid_json_file(temp_upload_dir: Path) -> Path:
    """
    Create an invalid JSON file for error testing.
    Crear un archivo JSON inválido para testing de errores.
    """
    file_path = temp_upload_dir / "invalid.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(INVALID_JSON, f, ensure_ascii=False, indent=2)
    return file_path


@pytest.fixture
def corrupted_file(temp_upload_dir: Path) -> Path:
    """
    Create a corrupted file for error testing.
    Crear un archivo corrupto para testing de errores.
    """
    file_path = temp_upload_dir / "corrupted.json"
    with open(file_path, "wb") as f:
        f.write(b"\x00\x01\x02\x03corrupted content")
    return file_path


@pytest.fixture
def sample_files(sample_json_file: Path, sample_json_file_2: Path) -> Dict[str, Path]:
    """
    Dictionary of sample test files.
    Diccionario de archivos de prueba de ejemplo.
    """
    return {
        "invoice_1": sample_json_file,
        "invoice_2": sample_json_file_2,
    }


@pytest.fixture
def json_bytes() -> BytesIO:
    """
    JSON content as BytesIO for upload testing.
    Contenido JSON como BytesIO para testing de upload.
    """
    content = json.dumps(SAMPLE_INVOICE_JSON, ensure_ascii=False).encode("utf-8")
    return BytesIO(content)


@pytest.fixture
def json_bytes_2() -> BytesIO:
    """
    Second JSON content as BytesIO for upload testing.
    Segundo contenido JSON como BytesIO para testing de upload.
    """
    content = json.dumps(SAMPLE_INVOICE_2_JSON, ensure_ascii=False).encode("utf-8")
    return BytesIO(content)


# ===========================================================================
# Helper Functions / Funciones Auxiliares
# ===========================================================================

def create_test_pdf(path: Path) -> Path:
    """
    Create a minimal valid PDF file for testing.
    Crear un archivo PDF mínimo válido para testing.

    Note: This creates a very basic PDF structure.
    Nota: Esto crea una estructura PDF muy básica.
    """
    # Minimal PDF content
    # Contenido PDF mínimo
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer
<< /Size 4 /Root 1 0 R >>
startxref
193
%%EOF"""

    with open(path, "wb") as f:
        f.write(pdf_content)

    return path


@pytest.fixture
def sample_pdf_file(temp_upload_dir: Path) -> Path:
    """
    Create a sample PDF file.
    Crear un archivo PDF de ejemplo.
    """
    file_path = temp_upload_dir / "sample.pdf"
    return create_test_pdf(file_path)


# ===========================================================================
# Cleanup Fixtures / Fixtures de Limpieza
# ===========================================================================

@pytest.fixture(autouse=True)
def clean_uploads(temp_upload_dir: Path):
    """
    Automatically clean up uploads after each test.
    Limpiar automáticamente uploads después de cada test.
    """
    yield

    # Cleanup is handled by temp_upload_dir fixture
    # La limpieza es manejada por el fixture temp_upload_dir


# ===========================================================================
# API Helper Fixtures / Fixtures Auxiliares de API
# ===========================================================================

@pytest.fixture
def api_headers() -> Dict[str, str]:
    """
    Common API headers for requests.
    Headers comunes de API para peticiones.
    """
    return {
        "Accept": "application/json",
    }


@pytest.fixture
def upload_headers() -> Dict[str, str]:
    """
    Headers for file upload requests.
    Headers para peticiones de carga de archivos.
    """
    return {
        "Accept": "application/json",
    }
