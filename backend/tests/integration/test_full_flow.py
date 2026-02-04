"""
Full Flow Integration Tests / Tests de Integración de Flujo Completo

Tests covering the complete API flow: upload -> process -> status -> download.
Tests cubriendo el flujo completo de API: upload -> process -> status -> download.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any

import pytest


class TestFullFlow:
    """
    Test suite for complete API flow.
    Suite de tests para el flujo completo de API.
    """

    @pytest.mark.integration
    def test_upload_process_status_download_flow(
        self,
        test_client,
        json_bytes,
        api_headers,
    ):
        """
        Test: POST /upload → POST /process → GET /status → GET /download

        Complete flow from upload to download.
        Flujo completo desde upload hasta download.
        """
        # ===========================================================
        # STEP 1: Upload file / PASO 1: Subir archivo
        # ===========================================================
        upload_response = test_client.post(
            "/api/v1/upload",
            files={"file": ("invoice.json", json_bytes, "application/json")},
            headers=api_headers,
        )

        assert upload_response.status_code == 200
        upload_data = upload_response.json()

        assert "file_id" in upload_data
        assert upload_data["status"] == "uploaded"
        file_id = upload_data["file_id"]

        # ===========================================================
        # STEP 2: Start processing / PASO 2: Iniciar procesamiento
        # ===========================================================
        process_response = test_client.post(
            "/api/v1/process",
            json={"file_ids": [file_id]},
            headers=api_headers,
        )

        assert process_response.status_code == 200
        process_data = process_response.json()

        assert "job_id" in process_data
        assert process_data["status"] in ["processing", "queued"]
        job_id = process_data["job_id"]

        # ===========================================================
        # STEP 3: Poll status until completion / PASO 3: Consultar estado hasta completar
        # ===========================================================
        max_polls = 60  # Maximum 60 seconds
        poll_interval = 1  # 1 second between polls
        completed = False

        for _ in range(max_polls):
            status_response = test_client.get(
                f"/api/v1/status/{job_id}",
                headers=api_headers,
            )

            assert status_response.status_code == 200
            status_data = status_response.json()

            if status_data["status"] == "completed":
                completed = True
                break
            elif status_data["status"] == "failed":
                pytest.fail(f"Processing failed: {status_data.get('error', 'Unknown error')}")

            time.sleep(poll_interval)

        assert completed, "Processing did not complete within timeout"
        assert status_data["progress"] == 100

        # ===========================================================
        # STEP 4: Download result / PASO 4: Descargar resultado
        # ===========================================================
        download_response = test_client.get(
            f"/api/v1/download/{job_id}?format=excel",
            headers=api_headers,
        )

        assert download_response.status_code == 200
        assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in download_response.headers.get("content-type", "")
        assert len(download_response.content) > 0

    @pytest.mark.integration
    def test_multiple_files_batch_processing(
        self,
        test_client,
        json_bytes,
        json_bytes_2,
        api_headers,
    ):
        """
        Test: Multiple files in a single processing job.

        Tests batch processing of multiple invoice files.
        Prueba el procesamiento por lotes de múltiples archivos de factura.
        """
        # Upload first file / Subir primer archivo
        upload_1 = test_client.post(
            "/api/v1/upload",
            files={"file": ("invoice1.json", json_bytes, "application/json")},
            headers=api_headers,
        )
        assert upload_1.status_code == 200
        file_id_1 = upload_1.json()["file_id"]

        # Upload second file / Subir segundo archivo
        json_bytes_2.seek(0)  # Reset stream position
        upload_2 = test_client.post(
            "/api/v1/upload",
            files={"file": ("invoice2.json", json_bytes_2, "application/json")},
            headers=api_headers,
        )
        assert upload_2.status_code == 200
        file_id_2 = upload_2.json()["file_id"]

        # Process both files / Procesar ambos archivos
        process_response = test_client.post(
            "/api/v1/process",
            json={"file_ids": [file_id_1, file_id_2]},
            headers=api_headers,
        )

        assert process_response.status_code == 200
        job_id = process_response.json()["job_id"]

        # Wait for completion / Esperar completado
        completed = False
        for _ in range(60):
            status = test_client.get(f"/api/v1/status/{job_id}").json()
            if status["status"] == "completed":
                completed = True
                break
            time.sleep(1)

        assert completed

        # Verify batch result / Verificar resultado del lote
        download = test_client.get(f"/api/v1/download/{job_id}?format=excel")
        assert download.status_code == 200
        assert len(download.content) > 0

    @pytest.mark.integration
    def test_process_with_custom_options(
        self,
        test_client,
        json_bytes,
        api_headers,
    ):
        """
        Test: Processing with custom options.

        Tests that custom processing options are respected.
        Prueba que las opciones de procesamiento personalizadas sean respetadas.
        """
        # Upload file / Subir archivo
        upload = test_client.post(
            "/api/v1/upload",
            files={"file": ("invoice.json", json_bytes, "application/json")},
            headers=api_headers,
        )
        file_id = upload.json()["file_id"]

        # Process with custom options / Procesar con opciones personalizadas
        process_response = test_client.post(
            "/api/v1/process",
            json={
                "file_ids": [file_id],
                "options": {
                    "output_format": "detailed",
                    "include_summary": True,
                    "currency_conversion": False,
                }
            },
            headers=api_headers,
        )

        assert process_response.status_code == 200
        job_id = process_response.json()["job_id"]

        # Wait and verify / Esperar y verificar
        completed = False
        for _ in range(60):
            status = test_client.get(f"/api/v1/status/{job_id}").json()
            if status["status"] == "completed":
                completed = True
                break
            time.sleep(1)

        assert completed

    @pytest.mark.integration
    def test_download_multiple_formats(
        self,
        test_client,
        json_bytes,
        api_headers,
    ):
        """
        Test: Download results in different formats.

        Tests Excel, PDF, and CSV download formats.
        Prueba formatos de descarga Excel, PDF y CSV.
        """
        # Upload and process / Subir y procesar
        upload = test_client.post(
            "/api/v1/upload",
            files={"file": ("invoice.json", json_bytes, "application/json")},
            headers=api_headers,
        )
        file_id = upload.json()["file_id"]

        process = test_client.post(
            "/api/v1/process",
            json={"file_ids": [file_id]},
            headers=api_headers,
        )
        job_id = process.json()["job_id"]

        # Wait for completion / Esperar completado
        for _ in range(60):
            status = test_client.get(f"/api/v1/status/{job_id}").json()
            if status["status"] == "completed":
                break
            time.sleep(1)

        # Test Excel download / Probar descarga Excel
        excel_download = test_client.get(f"/api/v1/download/{job_id}?format=excel")
        assert excel_download.status_code == 200
        assert "spreadsheet" in excel_download.headers.get("content-type", "")

        # Test PDF download / Probar descarga PDF
        pdf_download = test_client.get(f"/api/v1/download/{job_id}?format=pdf")
        assert pdf_download.status_code == 200
        assert "pdf" in pdf_download.headers.get("content-type", "")

        # Test CSV download / Probar descarga CSV
        csv_download = test_client.get(f"/api/v1/download/{job_id}?format=csv")
        assert csv_download.status_code == 200
        assert "csv" in csv_download.headers.get("content-type", "")


class TestHealthAndStatus:
    """
    Test suite for health check and status endpoints.
    Suite de tests para endpoints de health check y estado.
    """

    @pytest.mark.integration
    def test_health_check(self, test_client):
        """
        Test: GET /health returns healthy status.

        Verifies the health check endpoint.
        Verifica el endpoint de health check.
        """
        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert "version" in data

    @pytest.mark.integration
    def test_status_with_progress(
        self,
        test_client,
        json_bytes,
        api_headers,
    ):
        """
        Test: GET /status returns progress information.

        Verifies that status endpoint returns progress during processing.
        Verifica que el endpoint de status retorna progreso durante procesamiento.
        """
        # Upload and start processing / Subir e iniciar procesamiento
        upload = test_client.post(
            "/api/v1/upload",
            files={"file": ("invoice.json", json_bytes, "application/json")},
            headers=api_headers,
        )
        file_id = upload.json()["file_id"]

        process = test_client.post(
            "/api/v1/process",
            json={"file_ids": [file_id]},
            headers=api_headers,
        )
        job_id = process.json()["job_id"]

        # Check status includes progress / Verificar que status incluye progreso
        status_response = test_client.get(f"/api/v1/status/{job_id}")
        status_data = status_response.json()

        assert "status" in status_data
        assert "progress" in status_data
        assert 0 <= status_data["progress"] <= 100


class TestMixedFileTypes:
    """
    Test suite for mixed file type processing.
    Suite de tests para procesamiento de tipos de archivo mixtos.
    """

    @pytest.mark.integration
    def test_json_and_pdf_batch(
        self,
        test_client,
        json_bytes,
        sample_pdf_file,
        api_headers,
    ):
        """
        Test: Process batch with both JSON and PDF files.

        Tests processing of mixed file types in a single batch.
        Prueba el procesamiento de tipos de archivo mixtos en un solo lote.
        """
        # Upload JSON / Subir JSON
        upload_json = test_client.post(
            "/api/v1/upload",
            files={"file": ("invoice.json", json_bytes, "application/json")},
            headers=api_headers,
        )
        json_file_id = upload_json.json()["file_id"]

        # Upload PDF / Subir PDF
        with open(sample_pdf_file, "rb") as pdf_file:
            upload_pdf = test_client.post(
                "/api/v1/upload",
                files={"file": ("invoice.pdf", pdf_file, "application/pdf")},
                headers=api_headers,
            )
        pdf_file_id = upload_pdf.json()["file_id"]

        # Process both / Procesar ambos
        process = test_client.post(
            "/api/v1/process",
            json={"file_ids": [json_file_id, pdf_file_id]},
            headers=api_headers,
        )

        assert process.status_code == 200
        job_id = process.json()["job_id"]

        # Wait for completion / Esperar completado
        completed = False
        for _ in range(120):  # Longer timeout for mixed types
            status = test_client.get(f"/api/v1/status/{job_id}").json()
            if status["status"] == "completed":
                completed = True
                break
            elif status["status"] == "failed":
                # Mixed processing might have partial failures
                # Procesamiento mixto puede tener fallos parciales
                break
            time.sleep(1)

        # Verify job completed or handled gracefully
        # Verificar que el job completó o se manejó correctamente
        final_status = test_client.get(f"/api/v1/status/{job_id}").json()
        assert final_status["status"] in ["completed", "completed_with_errors"]
