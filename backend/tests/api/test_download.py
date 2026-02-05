"""
Download Endpoint Tests / Tests del Endpoint de Descarga
========================================================

Tests for the result download endpoint.
Tests para el endpoint de descarga de resultados.
"""

from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestDownloadEndpoint:
    """Tests for GET /api/download/{job_id} endpoint."""

    @pytest.fixture
    def pending_job_id(self):
        """Create a job that may still be processing."""
        content = b'{"document_number": "FAC-001", "customer_name": "Test", "issue_date": "2025-02-04", "subtotal": 100, "total": 100}'
        files = {"files": ("test.json", BytesIO(content), "application/json")}
        upload_resp = client.post("/api/upload", files=files)
        upload_id = upload_resp.json()["data"]["upload_id"]

        process_resp = client.post(
            "/api/process",
            json={"upload_id": upload_id, "output_format": "xlsx"},
        )
        return process_resp.json()["data"]["job_id"]

    def test_download_not_found(self):
        """Return 404 for non-existent job."""
        response = client.get("/api/download/non-existent-id")

        assert response.status_code == 404
        assert response.json()["error"] == "JOB_NOT_FOUND"

    def test_download_pending_job(self, pending_job_id):
        """Download may return 400 for pending/processing job or 200 if completed quickly."""
        response = client.get(f"/api/download/{pending_job_id}")

        # Job might complete quickly in tests, so accept both
        assert response.status_code in [200, 400]

        if response.status_code == 400:
            assert response.json()["error"] == "JOB_NOT_COMPLETED"
