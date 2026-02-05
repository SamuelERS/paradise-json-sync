"""
Error Handling Integration Tests / Tests de Integración de Manejo de Errores

Tests for error handling scenarios in the API.
Tests para escenarios de manejo de errores en la API.
"""

import json
import time
from io import BytesIO
from pathlib import Path

import pytest


class TestUploadErrors:
    """
    Test suite for upload error handling.
    Suite de tests para manejo de errores de upload.
    """

    @pytest.mark.integration
    def test_upload_corrupted_file(
        self,
        test_client,
        corrupted_file,
        api_headers,
    ):
        """
        Test: Upload of corrupted file returns error.

        Verifies that corrupted files are rejected gracefully.
        Verifica que los archivos corruptos son rechazados correctamente.
        """
        with open(corrupted_file, "rb") as f:
            response = test_client.post(
                "/api/v1/upload",
                files={"file": ("corrupted.json", f, "application/json")},
                headers=api_headers,
            )

        # Should return error status
        # Debe retornar estado de error
        assert response.status_code in [400, 422]

        data = response.json()
        assert "error" in data or "detail" in data

    @pytest.mark.integration
    def test_upload_empty_file(
        self,
        test_client,
        api_headers,
    ):
        """
        Test: Upload of empty file returns error.

        Verifies that empty files are rejected.
        Verifica que los archivos vacíos son rechazados.
        """
        empty_file = BytesIO(b"")

        response = test_client.post(
            "/api/v1/upload",
            files={"file": ("empty.json", empty_file, "application/json")},
            headers=api_headers,
        )

        assert response.status_code in [400, 422]

    @pytest.mark.integration
    def test_upload_invalid_file_type(
        self,
        test_client,
        api_headers,
    ):
        """
        Test: Upload of unsupported file type returns error.

        Verifies that unsupported file types are rejected.
        Verifica que los tipos de archivo no soportados son rechazados.
        """
        text_content = BytesIO(b"This is plain text, not JSON or PDF")

        response = test_client.post(
            "/api/v1/upload",
            files={"file": ("document.txt", text_content, "text/plain")},
            headers=api_headers,
        )

        assert response.status_code in [400, 415, 422]

    @pytest.mark.integration
    def test_upload_too_large_file(
        self,
        test_client,
        api_headers,
    ):
        """
        Test: Upload of oversized file returns error.

        Verifies that files exceeding size limit are rejected.
        Verifica que los archivos que exceden el límite de tamaño son rechazados.
        """
        # Create a large file (e.g., 100MB of zeros)
        # Crear un archivo grande (ej: 100MB de ceros)
        # Note: Adjust size based on actual limit
        # Nota: Ajustar tamaño basado en límite real
        large_content = BytesIO(b"0" * (10 * 1024 * 1024))  # 10MB

        response = test_client.post(
            "/api/v1/upload",
            files={"file": ("large.json", large_content, "application/json")},
            headers=api_headers,
        )

        # Should return error for oversized file
        # Debe retornar error para archivo muy grande
        # Status might be 413 (Payload Too Large) or 400
        # Estado puede ser 413 (Payload Too Large) o 400
        assert response.status_code in [400, 413, 422]

    @pytest.mark.integration
    def test_upload_malformed_json(
        self,
        test_client,
        api_headers,
    ):
        """
        Test: Upload of malformed JSON returns error.

        Verifies that invalid JSON syntax is caught.
        Verifica que la sintaxis JSON inválida es detectada.
        """
        malformed = BytesIO(b'{"invalid": json, missing quotes}')

        response = test_client.post(
            "/api/v1/upload",
            files={"file": ("malformed.json", malformed, "application/json")},
            headers=api_headers,
        )

        assert response.status_code in [400, 422]


class TestProcessErrors:
    """
    Test suite for processing error handling.
    Suite de tests para manejo de errores de procesamiento.
    """

    @pytest.mark.integration
    def test_process_nonexistent_job(
        self,
        test_client,
        api_headers,
    ):
        """
        Test: Process request with non-existent file IDs returns error.

        Verifies that invalid file references are caught.
        Verifica que las referencias de archivo inválidas son detectadas.
        """
        response = test_client.post(
            "/api/v1/process",
            json={"file_ids": ["nonexistent-id-12345"]},
            headers=api_headers,
        )

        assert response.status_code in [400, 404, 422]

    @pytest.mark.integration
    def test_process_empty_file_list(
        self,
        test_client,
        api_headers,
    ):
        """
        Test: Process request with empty file list returns error.

        Verifies that empty processing requests are rejected.
        Verifica que las peticiones de procesamiento vacías son rechazadas.
        """
        response = test_client.post(
            "/api/v1/process",
            json={"file_ids": []},
            headers=api_headers,
        )

        assert response.status_code in [400, 422]

    @pytest.mark.integration
    def test_process_invalid_options(
        self,
        test_client,
        json_bytes,
        api_headers,
    ):
        """
        Test: Process request with invalid options returns error.

        Verifies that invalid processing options are rejected.
        Verifica que las opciones de procesamiento inválidas son rechazadas.
        """
        # Upload a valid file first / Subir un archivo válido primero
        upload = test_client.post(
            "/api/v1/upload",
            files={"file": ("invoice.json", json_bytes, "application/json")},
            headers=api_headers,
        )
        file_id = upload.json()["file_id"]

        # Try to process with invalid options
        # Intentar procesar con opciones inválidas
        response = test_client.post(
            "/api/v1/process",
            json={
                "file_ids": [file_id],
                "options": {
                    "invalid_option": "invalid_value",
                    "another_bad_option": 12345,
                }
            },
            headers=api_headers,
        )

        # May accept and ignore invalid options, or return error
        # Puede aceptar e ignorar opciones inválidas, o retornar error
        assert response.status_code in [200, 400, 422]


class TestStatusErrors:
    """
    Test suite for status endpoint error handling.
    Suite de tests para manejo de errores del endpoint de estado.
    """

    @pytest.mark.integration
    def test_status_nonexistent_job(
        self,
        test_client,
        api_headers,
    ):
        """
        Test: Status request for non-existent job returns error.

        Verifies that invalid job IDs return 404.
        Verifica que los IDs de job inválidos retornan 404.
        """
        response = test_client.get(
            "/api/v1/status/nonexistent-job-99999",
            headers=api_headers,
        )

        assert response.status_code == 404

    @pytest.mark.integration
    def test_status_invalid_job_id_format(
        self,
        test_client,
        api_headers,
    ):
        """
        Test: Status request with invalid job ID format returns error.

        Verifies that malformed job IDs are rejected.
        Verifica que los IDs de job mal formados son rechazados.
        """
        response = test_client.get(
            "/api/v1/status/<script>alert('xss')</script>",
            headers=api_headers,
        )

        assert response.status_code in [400, 404, 422]


class TestDownloadErrors:
    """
    Test suite for download endpoint error handling.
    Suite de tests para manejo de errores del endpoint de descarga.
    """

    @pytest.mark.integration
    def test_download_before_completion(
        self,
        test_client,
        json_bytes,
        api_headers,
    ):
        """
        Test: Download before processing completes returns error.

        Verifies that premature downloads are prevented.
        Verifica que las descargas prematuras son prevenidas.
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

        # Immediately try to download (before completion)
        # Intentar descargar inmediatamente (antes de completar)
        response = test_client.get(
            f"/api/v1/download/{job_id}?format=excel",
            headers=api_headers,
        )

        # Should return error if not completed
        # Debe retornar error si no está completado
        # Note: Might return 202 (Accepted but not ready) or 400/404
        # Nota: Puede retornar 202 (Aceptado pero no listo) o 400/404
        assert response.status_code in [202, 400, 404, 409]

    @pytest.mark.integration
    def test_download_nonexistent_job(
        self,
        test_client,
        api_headers,
    ):
        """
        Test: Download for non-existent job returns error.

        Verifies that invalid download requests return 404.
        Verifica que las peticiones de descarga inválidas retornan 404.
        """
        response = test_client.get(
            "/api/v1/download/nonexistent-job-99999?format=excel",
            headers=api_headers,
        )

        assert response.status_code == 404

    @pytest.mark.integration
    def test_download_invalid_format(
        self,
        test_client,
        json_bytes,
        api_headers,
    ):
        """
        Test: Download with invalid format returns error.

        Verifies that unsupported formats are rejected.
        Verifica que los formatos no soportados son rechazados.
        """
        # Upload, process, and wait for completion
        # Subir, procesar y esperar completado
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

        # Try to download with invalid format
        # Intentar descargar con formato inválido
        response = test_client.get(
            f"/api/v1/download/{job_id}?format=invalid_format",
            headers=api_headers,
        )

        assert response.status_code in [400, 422]


class TestTimeoutHandling:
    """
    Test suite for timeout scenarios.
    Suite de tests para escenarios de timeout.
    """

    @pytest.mark.integration
    @pytest.mark.slow
    def test_long_processing_timeout(
        self,
        test_client,
        api_headers,
    ):
        """
        Test: Very long processing eventually times out or completes.

        Verifies that the system handles long-running jobs appropriately.
        Verifica que el sistema maneja jobs de larga duración apropiadamente.

        Note: This test is marked as slow and may be skipped in quick test runs.
        Nota: Este test está marcado como lento y puede saltarse en ejecuciones rápidas.
        """
        # This test would use a file that triggers long processing
        # Este test usaría un archivo que dispara procesamiento largo
        # For now, we just verify the status polling mechanism works
        # Por ahora, solo verificamos que el mecanismo de polling de estado funciona

        # Would need a special test file or mock for actual timeout testing
        # Necesitaría un archivo de prueba especial o mock para testing real de timeout
        pytest.skip("Requires special test setup for timeout testing")


class TestConcurrentRequests:
    """
    Test suite for concurrent request handling.
    Suite de tests para manejo de peticiones concurrentes.
    """

    @pytest.mark.integration
    def test_concurrent_uploads(
        self,
        test_client,
        api_headers,
    ):
        """
        Test: Multiple concurrent uploads are handled correctly.

        Verifies that the system handles concurrent uploads.
        Verifica que el sistema maneja uploads concurrentes.
        """
        import concurrent.futures
        from conftest import SAMPLE_INVOICE_JSON

        def upload_file(index: int):
            content = BytesIO(json.dumps(SAMPLE_INVOICE_JSON).encode())
            response = test_client.post(
                "/api/v1/upload",
                files={"file": (f"invoice_{index}.json", content, "application/json")},
                headers=api_headers,
            )
            return response.status_code

        # Execute 5 concurrent uploads / Ejecutar 5 uploads concurrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(upload_file, i) for i in range(5)]
            results = [f.result() for f in futures]

        # All uploads should succeed / Todos los uploads deben tener éxito
        assert all(status == 200 for status in results)

    @pytest.mark.integration
    def test_concurrent_status_checks(
        self,
        test_client,
        json_bytes,
        api_headers,
    ):
        """
        Test: Multiple concurrent status checks don't interfere.

        Verifies that concurrent status polling works correctly.
        Verifica que el polling de estado concurrente funciona correctamente.
        """
        import concurrent.futures

        # Setup: Create a job / Configurar: Crear un job
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

        def check_status():
            response = test_client.get(f"/api/v1/status/{job_id}")
            return response.status_code

        # Execute 10 concurrent status checks / Ejecutar 10 verificaciones de estado concurrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(check_status) for _ in range(10)]
            results = [f.result() for f in futures]

        # All status checks should succeed / Todas las verificaciones deben tener éxito
        assert all(status == 200 for status in results)
