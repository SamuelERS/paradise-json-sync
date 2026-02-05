"""
Upload Endpoint Tests / Tests del Endpoint de Subida
====================================================

Tests for the file upload endpoint.
Tests para el endpoint de subida de archivos.
"""

from io import BytesIO

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestUploadEndpoint:
    """Tests for POST /api/upload endpoint."""

    def test_upload_json_file(self):
        """Upload valid JSON file."""
        content = b'{"document_number": "001", "customer_name": "Test", "issue_date": "2025-02-04", "subtotal": 100, "total": 100}'
        files = {"files": ("test.json", BytesIO(content), "application/json")}

        response = client.post("/api/upload", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "upload_id" in data["data"]
        assert data["data"]["total_files"] == 1

    def test_upload_pdf_file(self):
        """Upload valid PDF file."""
        content = b"%PDF-1.4 fake pdf content"
        files = {"files": ("test.pdf", BytesIO(content), "application/pdf")}

        response = client.post("/api/upload", files=files)

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_upload_multiple_files(self):
        """Upload multiple files."""
        files = [
            ("files", ("test1.json", BytesIO(b'{"id": 1}'), "application/json")),
            ("files", ("test2.json", BytesIO(b'{"id": 2}'), "application/json")),
            ("files", ("test3.pdf", BytesIO(b"%PDF-1.4"), "application/pdf")),
        ]

        response = client.post("/api/upload", files=files)

        assert response.status_code == 200
        assert response.json()["data"]["total_files"] == 3

    def test_upload_invalid_extension(self):
        """Reject file with invalid extension."""
        files = {"files": ("test.txt", BytesIO(b"text content"), "text/plain")}

        response = client.post("/api/upload", files=files)

        assert response.status_code == 400
        assert response.json()["error"] == "INVALID_FILE_TYPE"

    def test_upload_file_too_large(self):
        """Reject file larger than 10MB."""
        content = b"x" * (11 * 1024 * 1024)  # 11MB
        files = {"files": ("big.json", BytesIO(content), "application/json")}

        response = client.post("/api/upload", files=files)

        assert response.status_code == 400
        assert response.json()["error"] == "FILE_TOO_LARGE"

    def test_upload_too_many_files(self):
        """Reject more than 50 files."""
        files = [
            ("files", (f"test{i}.json", BytesIO(b"{}"), "application/json")) for i in range(51)
        ]

        response = client.post("/api/upload", files=files)

        assert response.status_code == 400
        assert response.json()["error"] == "TOO_MANY_FILES"

    def test_upload_response_includes_file_info(self):
        """Upload response includes file information."""
        content = b'{"test": true}'
        files = {"files": ("invoice.json", BytesIO(content), "application/json")}

        response = client.post("/api/upload", files=files)
        data = response.json()

        assert len(data["data"]["files"]) == 1
        file_info = data["data"]["files"][0]
        assert file_info["name"] == "invoice.json"
        assert file_info["type"] == "json"
        assert file_info["size"] == len(content)

    def test_upload_response_includes_expiration(self):
        """Upload response includes expiration timestamp."""
        content = b'{"test": true}'
        files = {"files": ("test.json", BytesIO(content), "application/json")}

        response = client.post("/api/upload", files=files)
        data = response.json()

        assert "expires_at" in data["data"]
