"""
Purchase API Tests / Tests del API de Compras
===============================================

Integration tests for the purchase invoice API endpoints.
Tests de integracion para los endpoints del API de facturas de compra.

This module tests / Este modulo prueba:
- POST /api/purchases/upload: File upload validation
- POST /api/purchases/process: Async processing start
- GET /api/purchases/status/{job_id}: Status queries
- GET /api/purchases/formats: Format listing
- GET /api/purchases/columns: Column listing
- PurchaseProcessorService: Pipeline orchestration
"""

import json
import os
import tempfile
from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.services.purchase_service import PurchaseProcessorService

client = TestClient(app)


# === DTE Standard sample for service tests ===
SAMPLE_DTE_JSON = {
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
        "nombreComercial": "ABC Distribuciones",
        "codActividad": "47190",
    },
    "receptor": {
        "nit": "0614-999999-999-9",
        "nombre": "MI EMPRESA S.A. DE C.V.",
    },
    "cuerpoDocumento": [
        {
            "numItem": 1,
            "codigo": "PAP-001",
            "descripcion": "Papel Bond Carta Resma 500 hojas",
            "uniMedida": 59,
            "cantidad": 10,
            "precioUni": 3.50,
            "montoDescu": 0.00,
            "ventaGravada": 35.00,
            "ventaExenta": 0.00,
            "ventaNoSuj": 0.00,
            "ivaItem": 4.55,
        }
    ],
    "resumen": {
        "totalGravada": 35.00,
        "totalExenta": 0.00,
        "totalNoSuj": 0.00,
        "subTotal": 35.00,
        "totalDescu": 0.00,
        "totalIva": 4.55,
        "totalPagar": 39.55,
        "totalLetras": "TREINTA Y NUEVE 55/100 DOLARES",
        "condicionOperacion": 1,
    },
}


class TestPurchaseUpload:
    """Tests for POST /api/purchases/upload."""

    def test_upload_json_files(self):
        """Upload valid JSON files successfully."""
        content = json.dumps(SAMPLE_DTE_JSON).encode("utf-8")
        files = [
            ("files", ("factura1.json", BytesIO(content), "application/json")),
            ("files", ("factura2.json", BytesIO(content), "application/json")),
        ]

        response = client.post("/api/purchases/upload", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_files"] == 2
        assert data["data"]["json_count"] == 2
        assert data["data"]["pdf_count"] == 0
        assert "upload_id" in data["data"]

    def test_upload_mixed_files(self):
        """Upload mix of JSON and PDF files."""
        json_content = json.dumps({"test": True}).encode("utf-8")
        pdf_content = b"%PDF-1.4 fake pdf content for testing"

        files = [
            ("files", ("factura.json", BytesIO(json_content), "application/json")),
            ("files", ("factura.pdf", BytesIO(pdf_content), "application/pdf")),
        ]

        response = client.post("/api/purchases/upload", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["json_count"] == 1
        assert data["data"]["pdf_count"] == 1
        assert data["data"]["total_files"] == 2

    def test_upload_invalid_extension(self):
        """Reject files with invalid extensions."""
        files = {
            "files": ("data.txt", BytesIO(b"text content"), "text/plain")
        }

        response = client.post("/api/purchases/upload", files=files)

        assert response.status_code == 400
        assert response.json()["error"] == "INVALID_FILE_TYPE"

    def test_upload_empty_files(self):
        """Reject request with no files."""
        response = client.post("/api/purchases/upload")

        assert response.status_code == 422

    def test_upload_invalid_json_content(self):
        """Reject JSON file with invalid content."""
        files = {
            "files": (
                "bad.json",
                BytesIO(b"not valid json {{{"),
                "application/json",
            )
        }

        response = client.post("/api/purchases/upload", files=files)

        assert response.status_code == 400
        assert response.json()["error"] == "INVALID_FILE_TYPE"

    def test_upload_invalid_pdf_content(self):
        """Reject PDF file without PDF magic bytes."""
        files = {
            "files": (
                "fake.pdf",
                BytesIO(b"not a real pdf file"),
                "application/pdf",
            )
        }

        response = client.post("/api/purchases/upload", files=files)

        assert response.status_code == 400
        assert response.json()["error"] == "INVALID_FILE_TYPE"

    def test_upload_response_structure(self):
        """Verify upload response has correct structure."""
        content = json.dumps({"id": 1}).encode("utf-8")
        files = {
            "files": ("test.json", BytesIO(content), "application/json")
        }

        response = client.post("/api/purchases/upload", files=files)
        data = response.json()

        assert "success" in data
        assert "message" in data
        assert "data" in data
        assert "upload_id" in data["data"]
        assert "files" in data["data"]
        assert "total_files" in data["data"]
        assert "json_count" in data["data"]
        assert "pdf_count" in data["data"]
        assert "expires_at" in data["data"]


class TestPurchaseProcess:
    """Tests for POST /api/purchases/process."""

    def test_process_basic(self):
        """Start basic processing of uploaded files."""
        content = json.dumps(SAMPLE_DTE_JSON).encode("utf-8")
        files = [
            ("files", ("factura.json", BytesIO(content), "application/json")),
        ]
        upload_resp = client.post("/api/purchases/upload", files=files)
        upload_id = upload_resp.json()["data"]["upload_id"]

        response = client.post(
            "/api/purchases/process",
            json={
                "upload_id": upload_id,
                "output_format": "xlsx",
                "column_profile": "completo",
            },
        )

        assert response.status_code == 202
        data = response.json()
        assert data["success"] is True
        assert "job_id" in data["data"]
        assert data["data"]["status"] == "processing"

    def test_process_with_column_profile(self):
        """Process with specific column profile."""
        content = json.dumps(SAMPLE_DTE_JSON).encode("utf-8")
        files = [
            ("files", ("f.json", BytesIO(content), "application/json")),
        ]
        upload_resp = client.post("/api/purchases/upload", files=files)
        upload_id = upload_resp.json()["data"]["upload_id"]

        response = client.post(
            "/api/purchases/process",
            json={
                "upload_id": upload_id,
                "column_profile": "contador",
            },
        )

        assert response.status_code == 202

    def test_process_invalid_upload_id(self):
        """Reject processing with non-existent upload ID."""
        response = client.post(
            "/api/purchases/process",
            json={
                "upload_id": "non-existent-id",
                "output_format": "xlsx",
            },
        )

        assert response.status_code == 404
        assert response.json()["error"] == "UPLOAD_NOT_FOUND"

    def test_process_custom_without_columns(self):
        """Reject custom profile without custom_columns."""
        content = json.dumps({"test": 1}).encode("utf-8")
        files = [
            ("files", ("f.json", BytesIO(content), "application/json")),
        ]
        upload_resp = client.post("/api/purchases/upload", files=files)
        upload_id = upload_resp.json()["data"]["upload_id"]

        response = client.post(
            "/api/purchases/process",
            json={
                "upload_id": upload_id,
                "column_profile": "custom",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "INVALID_REQUEST"

    def test_process_custom_with_invalid_columns(self):
        """Reject custom profile with invalid column IDs."""
        content = json.dumps({"test": 1}).encode("utf-8")
        files = [
            ("files", ("f.json", BytesIO(content), "application/json")),
        ]
        upload_resp = client.post("/api/purchases/upload", files=files)
        upload_id = upload_resp.json()["data"]["upload_id"]

        response = client.post(
            "/api/purchases/process",
            json={
                "upload_id": upload_id,
                "column_profile": "custom",
                "custom_columns": ["total", "invalid_column"],
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "invalid_column" in data["message"]


class TestPurchaseStatus:
    """Tests for GET /api/purchases/status/{job_id}."""

    def test_status_not_found(self):
        """Return 404 for non-existent job ID."""
        response = client.get("/api/purchases/status/nonexistent-job")

        assert response.status_code == 404
        assert response.json()["error"] == "JOB_NOT_FOUND"

    def test_status_after_process(self):
        """Get status of a recently created job."""
        content = json.dumps(SAMPLE_DTE_JSON).encode("utf-8")
        files = [
            ("files", ("f.json", BytesIO(content), "application/json")),
        ]
        upload_resp = client.post("/api/purchases/upload", files=files)
        upload_id = upload_resp.json()["data"]["upload_id"]

        process_resp = client.post(
            "/api/purchases/process",
            json={"upload_id": upload_id},
        )
        job_id = process_resp.json()["data"]["job_id"]

        response = client.get(f"/api/purchases/status/{job_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["job_id"] == job_id


class TestPurchaseDownload:
    """Tests for GET /api/purchases/download/{job_id}."""

    def test_download_not_found(self):
        """Return 404 for non-existent job."""
        response = client.get("/api/purchases/download/nonexistent")

        assert response.status_code == 404

    def test_download_not_completed(self):
        """Return 400 for job that is not completed."""
        content = json.dumps(SAMPLE_DTE_JSON).encode("utf-8")
        files = [
            ("files", ("f.json", BytesIO(content), "application/json")),
        ]
        upload_resp = client.post("/api/purchases/upload", files=files)
        upload_id = upload_resp.json()["data"]["upload_id"]

        process_resp = client.post(
            "/api/purchases/process",
            json={"upload_id": upload_id},
        )
        job_id = process_resp.json()["data"]["job_id"]

        response = client.get(f"/api/purchases/download/{job_id}")

        assert response.status_code in (400, 404)


class TestPurchaseEndpoints:
    """Tests for GET /api/purchases/formats and /columns."""

    def test_list_formats(self):
        """List supported purchase invoice formats."""
        response = client.get("/api/purchases/formats")

        assert response.status_code == 200
        data = response.json()
        assert "formats" in data
        formats = data["formats"]
        assert len(formats) >= 4

        format_ids = [f["id"] for f in formats]
        assert "DTE_STANDARD" in format_ids
        assert "DTE_VARIANT_A" in format_ids
        assert "GENERIC_FLAT" in format_ids
        assert "PDF_EXTRACTED" in format_ids

        for fmt in formats:
            assert "id" in fmt
            assert "name" in fmt
            assert "description" in fmt

    def test_list_columns(self):
        """List available columns and profiles."""
        response = client.get("/api/purchases/columns")

        assert response.status_code == 200
        data = response.json()
        assert "profiles" in data
        assert "all_columns" in data

        profiles = data["profiles"]
        assert "basico" in profiles
        assert "completo" in profiles
        assert "contador" in profiles

        assert "columns" in profiles["basico"]
        assert "total" in profiles["basico"]["columns"]

        all_cols = data["all_columns"]
        assert len(all_cols) >= 9
        col_ids = [c["id"] for c in all_cols]
        assert "control_number" in col_ids
        assert "total" in col_ids
        assert "tax" in col_ids

        for col in all_cols:
            assert "id" in col
            assert "label" in col
            assert "category" in col


class TestPurchaseProcessorService:
    """Tests for PurchaseProcessorService pipeline."""

    def test_process_single_json(self, tmp_path):
        """Process a single valid DTE JSON file."""
        json_file = tmp_path / "factura.json"
        json_file.write_text(
            json.dumps(SAMPLE_DTE_JSON), encoding="utf-8"
        )

        service = PurchaseProcessorService()
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            service.process(
                file_paths=[str(json_file)],
                config=None,
            )
        )

        assert result.invoice_count >= 1
        assert result.error_count == 0
        assert len(result.errors) == 0

    def test_process_invalid_json(self, tmp_path):
        """Process invalid JSON generates error."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not valid json {{{", encoding="utf-8")

        service = PurchaseProcessorService()
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            service.process(
                file_paths=[str(bad_file)],
                config=None,
            )
        )

        assert result.error_count == 1
        assert result.invoice_count == 0
        assert len(result.errors) == 1

    def test_process_unknown_format(self, tmp_path):
        """Process unknown format uses fallback mapper."""
        unknown_data = {
            "numero_factura": "F-001",
            "fecha": "2026-02-06",
            "proveedor": "ABC S.A.",
            "nit_proveedor": "0614-123456-789-0",
            "items": [
                {
                    "descripcion": "Producto X",
                    "cantidad": 2,
                    "precio": 10.00,
                    "total": 20.00,
                }
            ],
            "total": 20.00,
        }
        json_file = tmp_path / "generic.json"
        json_file.write_text(
            json.dumps(unknown_data), encoding="utf-8"
        )

        service = PurchaseProcessorService()
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            service.process(
                file_paths=[str(json_file)],
                config=None,
            )
        )

        # Should process (possibly with warnings) or error gracefully
        assert result.invoice_count + result.error_count == 1

    def test_load_json_valid(self, tmp_path):
        """Load and parse valid JSON file."""
        data = {"key": "value", "number": 42}
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(data), encoding="utf-8")

        service = PurchaseProcessorService()
        loaded = service._load_json(str(json_file))

        assert loaded == data
        assert loaded["key"] == "value"
        assert loaded["number"] == 42

    def test_load_json_invalid(self, tmp_path):
        """Loading invalid JSON raises JSONDecodeError."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not json {{", encoding="utf-8")

        service = PurchaseProcessorService()
        with pytest.raises(json.JSONDecodeError):
            service._load_json(str(bad_file))

    def test_count_formats(self):
        """Count detected formats from invoices."""
        from src.models.purchase_invoice import (
            PurchaseInvoice,
            SupplierInfo,
        )
        from datetime import date
        from decimal import Decimal

        invoices = []
        for i, fmt in enumerate(["DTE_STANDARD", "DTE_STANDARD", "GENERIC_FLAT"]):
            inv = PurchaseInvoice(
                document_number=f"DOC-{i}",
                issue_date=date(2026, 2, 6),
                supplier=SupplierInfo(name=f"Supplier {i}"),
                total=Decimal("100"),
                detected_format=fmt,
            )
            invoices.append(inv)

        counts = PurchaseProcessorService._count_formats(invoices)

        assert counts["DTE_STANDARD"] == 2
        assert counts["GENERIC_FLAT"] == 1

    def test_process_with_progress_callback(self, tmp_path):
        """Process files with progress callback."""
        json_file = tmp_path / "factura.json"
        json_file.write_text(
            json.dumps(SAMPLE_DTE_JSON), encoding="utf-8"
        )

        progress_calls = []

        def callback(current, total, msg):
            progress_calls.append((current, total, msg))

        service = PurchaseProcessorService()
        import asyncio
        asyncio.get_event_loop().run_until_complete(
            service.process(
                file_paths=[str(json_file)],
                config=None,
                progress_callback=callback,
            )
        )

        assert len(progress_calls) == 1
        assert progress_calls[0][0] == 1
        assert progress_calls[0][1] == 1

    def test_process_multiple_files(self, tmp_path):
        """Process multiple JSON files."""
        files = []
        for i in range(3):
            data = SAMPLE_DTE_JSON.copy()
            data = json.loads(json.dumps(SAMPLE_DTE_JSON))
            data["identificacion"]["codigoGeneracion"] = (
                f"A1B2C3D4-E5F6-7890-ABCD-EF12345678{i:02d}"
            )
            data["identificacion"]["numeroControl"] = (
                f"DTE-03-0000000{i+1}-00000000000000{i+1}"
            )
            f = tmp_path / f"factura_{i}.json"
            f.write_text(json.dumps(data), encoding="utf-8")
            files.append(str(f))

        service = PurchaseProcessorService()
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            service.process(file_paths=files, config=None)
        )

        assert result.invoice_count + result.error_count == 3
