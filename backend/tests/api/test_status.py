"""
Status Endpoint Tests / Tests del Endpoint de Estado
====================================================

Tests for the job status endpoint.
Tests para el endpoint de estado de trabajos.
"""

from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestStatusEndpoint:
    """Tests for GET /api/status/{job_id} endpoint."""

    @pytest.fixture
    def job_id(self):
        """Create a job for testing."""
        # First upload
        content = b'{"document_number": "FAC-001", "customer_name": "Test", "issue_date": "2025-02-04", "subtotal": 100, "total": 100}'
        files = {"files": ("test.json", BytesIO(content), "application/json")}
        upload_resp = client.post("/api/upload", files=files)
        upload_id = upload_resp.json()["data"]["upload_id"]

        # Then process
        process_resp = client.post(
            "/api/process",
            json={"upload_id": upload_id, "output_format": "xlsx"},
        )
        return process_resp.json()["data"]["job_id"]

    def test_status_not_found(self):
        """Return 404 for non-existent job."""
        response = client.get("/api/status/non-existent-id")

        assert response.status_code == 404
        assert response.json()["error"] == "JOB_NOT_FOUND"

    def test_status_returns_job_info(self, job_id):
        """Return job information."""
        response = client.get(f"/api/status/{job_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["job_id"] == job_id

    def test_status_includes_progress(self, job_id):
        """Status includes progress percentage."""
        response = client.get(f"/api/status/{job_id}")
        data = response.json()

        assert "progress" in data["data"]
        assert 0 <= data["data"]["progress"] <= 100

    def test_status_includes_status_field(self, job_id):
        """Status includes status field."""
        response = client.get(f"/api/status/{job_id}")
        data = response.json()

        assert "status" in data["data"]
        assert data["data"]["status"] in ["pending", "processing", "completed", "failed"]
