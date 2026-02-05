"""
Process Formats Integration Tests / Tests de Integración de Formatos
=====================================================================

Integration tests for all output formats.
Tests de integración para todos los formatos de salida.
"""

from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestProcessFormats:
    """Tests for different output format processing / Tests para procesamiento de diferentes formatos."""

    @pytest.fixture
    def upload_id(self):
        """Create an upload for testing / Crea un upload para testing."""
        content = b'{"document_number": "FAC-001", "customer_name": "Test Customer", "issue_date": "2025-02-04", "subtotal": 100, "total": 100}'
        files = {"files": ("test.json", BytesIO(content), "application/json")}
        response = client.post("/api/upload", files=files)
        return response.json()["data"]["upload_id"]

    def test_process_xlsx_format(self, upload_id):
        """Process with xlsx format / Procesa con formato xlsx."""
        response = client.post(
            "/api/process",
            json={"upload_id": upload_id, "output_format": "xlsx"},
        )
        assert response.status_code == 202
        data = response.json()
        assert data["success"] is True
        assert "job_id" in data["data"]

    def test_process_csv_format(self, upload_id):
        """Process with csv format / Procesa con formato csv."""
        response = client.post(
            "/api/process",
            json={"upload_id": upload_id, "output_format": "csv"},
        )
        assert response.status_code == 202
        data = response.json()
        assert data["success"] is True
        assert "job_id" in data["data"]

    def test_process_pdf_format(self, upload_id):
        """Process with pdf format / Procesa con formato pdf."""
        response = client.post(
            "/api/process",
            json={"upload_id": upload_id, "output_format": "pdf"},
        )
        assert response.status_code == 202
        data = response.json()
        assert data["success"] is True
        assert "job_id" in data["data"]

    def test_process_json_format(self, upload_id):
        """Process with json format / Procesa con formato json."""
        response = client.post(
            "/api/process",
            json={"upload_id": upload_id, "output_format": "json"},
        )
        assert response.status_code == 202
        data = response.json()
        assert data["success"] is True
        assert "job_id" in data["data"]

    def test_process_invalid_format_rejected(self, upload_id):
        """Reject invalid output format / Rechaza formato de salida inválido."""
        response = client.post(
            "/api/process",
            json={"upload_id": upload_id, "output_format": "doc"},
        )
        assert response.status_code == 422  # Validation error
