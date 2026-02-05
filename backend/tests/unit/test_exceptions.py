"""
Exception Tests / Pruebas de Excepciones
========================================

Unit tests for API exception classes and handlers.
Pruebas unitarias para clases de excepciones del API.
"""

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from src.api.exceptions import (
    APIException,
    FileTooLargeError,
    InvalidFileTypeError,
    JobNotCompletedError,
    JobNotFoundError,
    TooManyFilesError,
    UploadNotFoundError,
    setup_exception_handlers,
)


class TestAPIException:
    """Tests for base APIException class."""

    def test_creates_with_default_status(self):
        """Test exception creates with default 400 status."""
        exc = APIException(error="TEST_ERROR", message="Test message")

        assert exc.error == "TEST_ERROR"
        assert exc.message == "Test message"
        assert exc.status_code == 400

    def test_creates_with_custom_status(self):
        """Test exception creates with custom status code."""
        exc = APIException(error="NOT_FOUND", message="Resource not found", status_code=404)

        assert exc.status_code == 404

    def test_str_returns_message(self):
        """Test str() returns the message."""
        exc = APIException(error="ERROR", message="Error message")

        assert str(exc) == "Error message"


class TestUploadNotFoundError:
    """Tests for UploadNotFoundError."""

    def test_creates_with_upload_id(self):
        """Test exception includes upload_id in message."""
        exc = UploadNotFoundError(upload_id="upload-123")

        assert exc.error == "UPLOAD_NOT_FOUND"
        assert "upload-123" in exc.message
        assert exc.status_code == 404


class TestJobNotFoundError:
    """Tests for JobNotFoundError."""

    def test_creates_with_job_id(self):
        """Test exception includes job_id in message."""
        exc = JobNotFoundError(job_id="job-456")

        assert exc.error == "JOB_NOT_FOUND"
        assert "job-456" in exc.message
        assert exc.status_code == 404


class TestJobNotCompletedError:
    """Tests for JobNotCompletedError."""

    def test_creates_with_job_id_and_status(self):
        """Test exception includes job_id and status in message."""
        exc = JobNotCompletedError(job_id="job-789", status="processing")

        assert exc.error == "JOB_NOT_COMPLETED"
        assert "job-789" in exc.message
        assert "processing" in exc.message
        assert exc.status_code == 400


class TestInvalidFileTypeError:
    """Tests for InvalidFileTypeError."""

    def test_creates_with_filename_and_allowed(self):
        """Test exception includes filename and allowed types."""
        exc = InvalidFileTypeError(
            filename="document.txt",
            allowed=[".json", ".pdf"],
        )

        assert exc.error == "INVALID_FILE_TYPE"
        assert "document.txt" in exc.message
        assert ".json" in exc.message
        assert ".pdf" in exc.message
        assert exc.status_code == 400

    def test_includes_detail_when_provided(self):
        """Test exception includes detail message when provided."""
        exc = InvalidFileTypeError(
            filename="test.exe",
            allowed=[".json"],
            detail="Executable files are not allowed",
        )

        assert "Executable files are not allowed" in exc.message


class TestFileTooLargeError:
    """Tests for FileTooLargeError."""

    def test_creates_with_filename_and_max_size(self):
        """Test exception includes filename and max size."""
        exc = FileTooLargeError(filename="large.pdf", max_size_mb=10)

        assert exc.error == "FILE_TOO_LARGE"
        assert "large.pdf" in exc.message
        assert "10" in exc.message
        assert exc.status_code == 400


class TestTooManyFilesError:
    """Tests for TooManyFilesError."""

    def test_creates_with_count_and_max(self):
        """Test exception includes count and max files."""
        exc = TooManyFilesError(count=150, max_files=100)

        assert exc.error == "TOO_MANY_FILES"
        assert "150" in exc.message
        assert "100" in exc.message
        assert exc.status_code == 400


class TestExceptionHandlers:
    """Tests for exception handlers setup."""

    @pytest.fixture
    def app(self):
        """Create test FastAPI app with exception handlers."""
        app = FastAPI()
        setup_exception_handlers(app)

        @app.get("/api-exception")
        async def raise_api_exception():
            raise APIException(error="TEST_ERROR", message="Test error", status_code=400)

        @app.get("/upload-not-found")
        async def raise_upload_not_found():
            raise UploadNotFoundError(upload_id="test-upload")

        @app.get("/http-exception")
        async def raise_http_exception():
            raise HTTPException(status_code=403, detail="Forbidden")

        @app.get("/http-exception-dict")
        async def raise_http_exception_dict():
            raise HTTPException(
                status_code=400,
                detail={"error": "CUSTOM_ERROR", "message": "Custom message"},
            )

        @app.get("/general-exception")
        async def raise_general_exception():
            raise ValueError("Unexpected error")

        return app

    @pytest.fixture
    def client(self, app):
        """Test client for the app."""
        return TestClient(app, raise_server_exceptions=False)

    def test_handles_api_exception(self, client):
        """Test API exception handler returns correct response."""
        response = client.get("/api-exception")

        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "TEST_ERROR"
        assert data["message"] == "Test error"

    def test_handles_upload_not_found(self, client):
        """Test specific API exceptions are handled."""
        response = client.get("/upload-not-found")

        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "UPLOAD_NOT_FOUND"

    def test_handles_http_exception_string(self, client):
        """Test HTTP exception with string detail."""
        response = client.get("/http-exception")

        assert response.status_code == 403
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "HTTP_ERROR"
        assert data["message"] == "Forbidden"

    def test_handles_http_exception_dict(self, client):
        """Test HTTP exception with dict detail."""
        response = client.get("/http-exception-dict")

        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "CUSTOM_ERROR"

    def test_handles_general_exception(self, client):
        """Test general exception returns 500 error."""
        response = client.get("/general-exception")

        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "INTERNAL_ERROR"
