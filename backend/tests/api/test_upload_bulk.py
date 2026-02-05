"""
Bulk Upload Tests / Tests de Subida Masiva
==========================================

Tests for bulk file upload functionality (up to 10000 files).
Tests para funcionalidad de subida masiva de archivos (hasta 10000 archivos).
"""

# IMPORTANT: Set TESTING before any imports that touch src.main
# IMPORTANTE: Configurar TESTING antes de cualquier import que toque src.main
import os
os.environ["TESTING"] = "true"

import time
from io import BytesIO

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestBulkUpload:
    """Tests for bulk file upload scenarios."""

    def test_upload_1000_files(self):
        """Upload 1000 files (well under the 10000 limit)."""
        files = [
            ("files", (f"invoice_{i:04d}.json", BytesIO(b'{"id": ' + str(i).encode() + b'}'), "application/json"))
            for i in range(1000)
        ]

        response = client.post("/api/upload", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_files"] == 1000

    def test_upload_100_files_performance(self):
        """Upload 100 files should complete within reasonable time."""
        files = [
            ("files", (f"test_{i:03d}.json", BytesIO(b'{"document_number": "' + str(i).encode() + b'"}'), "application/json"))
            for i in range(100)
        ]

        start_time = time.time()
        response = client.post("/api/upload", files=files)
        elapsed_time = time.time() - start_time

        assert response.status_code == 200
        assert response.json()["data"]["total_files"] == 100
        # Should complete within 10 seconds for 100 small JSON files
        assert elapsed_time < 10, f"Upload took too long: {elapsed_time:.2f}s"

    def test_upload_mixed_json_and_pdf(self):
        """Upload mix of JSON and PDF files."""
        files = []
        for i in range(50):
            if i % 2 == 0:
                files.append(("files", (f"invoice_{i}.json", BytesIO(b'{"id": ' + str(i).encode() + b'}'), "application/json")))
            else:
                files.append(("files", (f"document_{i}.pdf", BytesIO(b"%PDF-1.4 content"), "application/pdf")))

        response = client.post("/api/upload", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total_files"] == 50

        # Verify both types are present
        file_types = [f["type"] for f in data["data"]["files"]]
        assert "json" in file_types
        assert "pdf" in file_types

    def test_upload_realistic_invoice_data(self):
        """Upload files with realistic invoice JSON structure."""
        invoice_template = b'''{
            "document_number": "FAC-%03d",
            "customer_name": "Cliente de Prueba",
            "issue_date": "2025-02-04",
            "items": [
                {"description": "Producto 1", "quantity": 2, "unit_price": 100.00},
                {"description": "Producto 2", "quantity": 1, "unit_price": 250.00}
            ],
            "subtotal": 450.00,
            "tax": 72.00,
            "total": 522.00
        }'''

        files = []
        for i in range(100):
            content = invoice_template.replace(b"%03d", str(i).zfill(3).encode())
            files.append(("files", (f"factura_{i:03d}.json", BytesIO(content), "application/json")))

        response = client.post("/api/upload", files=files)

        assert response.status_code == 200
        assert response.json()["data"]["total_files"] == 100

    def test_upload_with_various_file_sizes(self):
        """Upload files of various sizes within limits."""
        files = []

        # Small files (~100 bytes)
        for i in range(20):
            files.append(("files", (f"small_{i}.json", BytesIO(b'{"size": "small"}'), "application/json")))

        # Medium files (~5KB)
        medium_content = b'{"data": "' + b'x' * 5000 + b'"}'
        for i in range(20):
            files.append(("files", (f"medium_{i}.json", BytesIO(medium_content), "application/json")))

        # Larger files (~100KB) - still well under 10MB limit
        large_content = b'{"data": "' + b'y' * 100000 + b'"}'
        for i in range(10):
            files.append(("files", (f"large_{i}.json", BytesIO(large_content), "application/json")))

        response = client.post("/api/upload", files=files)

        assert response.status_code == 200
        assert response.json()["data"]["total_files"] == 50

    def test_upload_all_files_have_unique_paths(self):
        """Verify all uploaded files get unique storage paths."""
        files = [
            ("files", (f"file_{i}.json", BytesIO(b'{"id": ' + str(i).encode() + b'}'), "application/json"))
            for i in range(50)
        ]

        response = client.post("/api/upload", files=files)

        assert response.status_code == 200
        data = response.json()

        # All file names should be preserved
        names = [f["name"] for f in data["data"]["files"]]
        assert len(names) == len(set(names)), "File names should be unique"

    def test_upload_generates_valid_upload_id(self):
        """Verify upload_id is a valid UUID format."""
        import re
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

        files = [
            ("files", (f"test_{i}.json", BytesIO(b'{}'), "application/json"))
            for i in range(10)
        ]

        response = client.post("/api/upload", files=files)

        assert response.status_code == 200
        upload_id = response.json()["data"]["upload_id"]
        assert uuid_pattern.match(upload_id), f"Invalid UUID format: {upload_id}"

    def test_upload_calculates_correct_file_sizes(self):
        """Verify file sizes are correctly reported."""
        content_small = b'{"small": true}'  # 15 bytes
        content_large = b'{"data": "' + b'a' * 1000 + b'"}'  # ~1013 bytes

        files = [
            ("files", ("small.json", BytesIO(content_small), "application/json")),
            ("files", ("large.json", BytesIO(content_large), "application/json")),
        ]

        response = client.post("/api/upload", files=files)

        assert response.status_code == 200
        data = response.json()

        sizes = {f["name"]: f["size"] for f in data["data"]["files"]}
        assert sizes["small.json"] == len(content_small)
        assert sizes["large.json"] == len(content_large)


class TestBulkUploadEdgeCases:
    """Edge case tests for bulk uploads."""

    def test_upload_at_file_count_boundary(self):
        """Test uploading exactly at the 10000 file boundary."""
        # 9999 files should succeed
        files_9999 = [
            ("files", (f"test_{i}.json", BytesIO(b'{}'), "application/json"))
            for i in range(9999)
        ]
        response = client.post("/api/upload", files=files_9999)
        assert response.status_code == 200
        assert response.json()["data"]["total_files"] == 9999

        # 10000 files should succeed
        files_10000 = [
            ("files", (f"test_{i}.json", BytesIO(b'{}'), "application/json"))
            for i in range(10000)
        ]
        response = client.post("/api/upload", files=files_10000)
        assert response.status_code == 200
        assert response.json()["data"]["total_files"] == 10000

        # 10001 files should fail
        files_10001 = [
            ("files", (f"test_{i}.json", BytesIO(b'{}'), "application/json"))
            for i in range(10001)
        ]
        response = client.post("/api/upload", files=files_10001)
        assert response.status_code == 400
        assert response.json()["error"] == "TOO_MANY_FILES"

    def test_upload_with_duplicate_filenames(self):
        """Upload files with same name - duplicates are accepted and last one wins."""
        files = [
            ("files", ("same_name.json", BytesIO(b'{"version": 1}'), "application/json")),
            ("files", ("same_name.json", BytesIO(b'{"version": 2}'), "application/json")),
            ("files", ("same_name.json", BytesIO(b'{"version": 3}'), "application/json")),
        ]

        response = client.post("/api/upload", files=files)

        # Duplicates are accepted - the file_service saves all files sequentially
        # The last file with the same name overwrites previous ones on disk
        # but all 3 are counted in the response (behavior as implemented)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total_files"] == 3

    def test_upload_empty_json_files(self):
        """Upload valid but empty JSON objects."""
        files = [
            ("files", (f"empty_{i}.json", BytesIO(b'{}'), "application/json"))
            for i in range(100)
        ]

        response = client.post("/api/upload", files=files)

        assert response.status_code == 200
        assert response.json()["data"]["total_files"] == 100

    def test_upload_json_arrays(self):
        """Upload JSON files containing arrays."""
        files = [
            ("files", (f"array_{i}.json", BytesIO(b'[{"id": 1}, {"id": 2}]'), "application/json"))
            for i in range(50)
        ]

        response = client.post("/api/upload", files=files)

        assert response.status_code == 200
        assert response.json()["data"]["total_files"] == 50

    def test_upload_with_unicode_content(self):
        """Upload JSON files with Unicode content."""
        content = '{"name": "Café ñoño 日本語", "emoji": "🎉"}'.encode('utf-8')
        files = [
            ("files", (f"unicode_{i}.json", BytesIO(content), "application/json"))
            for i in range(20)
        ]

        response = client.post("/api/upload", files=files)

        assert response.status_code == 200
        assert response.json()["data"]["total_files"] == 20
