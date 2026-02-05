"""
Process Endpoint Tests / Tests del Endpoint de Procesamiento
============================================================

Tests for the file processing endpoint.
Tests para el endpoint de procesamiento de archivos.
"""

from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestProcessEndpoint:
    """Tests for POST /api/process endpoint."""

    @pytest.fixture
    def upload_id(self):
        """Create an upload for testing."""
        content = b'{"document_number": "FAC-001", "customer_name": "Test Customer", "issue_date": "2025-02-04", "subtotal": 100, "total": 100}'
        files = {"files": ("test.json", BytesIO(content), "application/json")}
        response = client.post("/api/upload", files=files)
        return response.json()["data"]["upload_id"]

    def test_process_valid_upload(self, upload_id):
        """Process valid upload returns 202."""
        response = client.post(
            "/api/process",
            json={"upload_id": upload_id, "output_format": "xlsx"},
        )

        assert response.status_code == 202
        data = response.json()
        assert data["success"] is True
        assert "job_id" in data["data"]
        assert data["data"]["status"] == "processing"

    def test_process_with_options(self, upload_id):
        """Process with custom options."""
        response = client.post(
            "/api/process",
            json={
                "upload_id": upload_id,
                "output_format": "xlsx",
                "options": {
                    "include_summary": True,
                    "group_by": "date",
                },
            },
        )

        assert response.status_code == 202

    def test_process_invalid_upload(self):
        """Reject non-existent upload."""
        response = client.post(
            "/api/process",
            json={"upload_id": "non-existent-id", "output_format": "xlsx"},
        )

        assert response.status_code == 404
        assert response.json()["error"] == "UPLOAD_NOT_FOUND"

    def test_process_invalid_format_rejected(self, upload_id):
        """Reject invalid output format."""
        response = client.post(
            "/api/process",
            json={"upload_id": upload_id, "output_format": "doc"},
        )

        assert response.status_code == 422  # Validation error

    def test_process_returns_estimated_time(self, upload_id):
        """Process response includes estimated time."""
        response = client.post(
            "/api/process",
            json={"upload_id": upload_id},
        )
        data = response.json()

        assert "estimated_time" in data["data"]
        assert data["data"]["estimated_time"] > 0

    def test_process_returns_created_at(self, upload_id):
        """Process response includes creation timestamp."""
        response = client.post(
            "/api/process",
            json={"upload_id": upload_id},
        )
        data = response.json()

        assert "created_at" in data["data"]
