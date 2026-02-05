"""
Schema Tests / Pruebas de Esquemas
==================================

Unit tests for Pydantic schemas.
Pruebas unitarias para esquemas Pydantic.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.api.schemas.process import ProcessData, ProcessOptions, ProcessRequest, ProcessResponse
from src.api.schemas.responses import ErrorResponse, HealthResponse
from src.api.schemas.status import JobData, JobResult, StatusResponse
from src.api.schemas.upload import FileInfo, UploadData, UploadResponse


class TestFileInfo:
    """Tests for FileInfo schema."""

    def test_creates_valid_file_info(self):
        """Test creating valid FileInfo."""
        info = FileInfo(name="test.json", size=1024, type="json")

        assert info.name == "test.json"
        assert info.size == 1024
        assert info.type == "json"

    def test_requires_all_fields(self):
        """Test that all fields are required."""
        with pytest.raises(ValidationError):
            FileInfo(name="test.json")

        with pytest.raises(ValidationError):
            FileInfo(name="test.json", size=100)


class TestUploadData:
    """Tests for UploadData schema."""

    def test_creates_valid_upload_data(self):
        """Test creating valid UploadData."""
        now = datetime.utcnow()
        data = UploadData(
            upload_id="upload-123",
            files=[FileInfo(name="test.json", size=100, type="json")],
            total_files=1,
            expires_at=now,
        )

        assert data.upload_id == "upload-123"
        assert len(data.files) == 1
        assert data.total_files == 1

    def test_files_list_validation(self):
        """Test files list contains valid FileInfo objects."""
        now = datetime.utcnow()
        data = UploadData(
            upload_id="upload-123",
            files=[
                FileInfo(name="a.json", size=100, type="json"),
                FileInfo(name="b.pdf", size=200, type="pdf"),
            ],
            total_files=2,
            expires_at=now,
        )

        assert data.files[0].name == "a.json"
        assert data.files[1].name == "b.pdf"


class TestUploadResponse:
    """Tests for UploadResponse schema."""

    def test_creates_valid_response(self):
        """Test creating valid UploadResponse."""
        now = datetime.utcnow()
        response = UploadResponse(
            success=True,
            message="Upload successful",
            data=UploadData(
                upload_id="upload-123",
                files=[],
                total_files=0,
                expires_at=now,
            ),
        )

        assert response.success is True
        assert response.message == "Upload successful"


class TestProcessOptions:
    """Tests for ProcessOptions schema."""

    def test_default_values(self):
        """Test default values are set."""
        options = ProcessOptions()

        assert options.include_summary is True
        assert options.group_by == "none"

    def test_custom_values(self):
        """Test setting custom values."""
        options = ProcessOptions(include_summary=False, group_by="date")

        assert options.include_summary is False
        assert options.group_by == "date"

    def test_group_by_validation(self):
        """Test group_by only accepts valid values."""
        ProcessOptions(group_by="date")
        ProcessOptions(group_by="vendor")
        ProcessOptions(group_by="none")

        with pytest.raises(ValidationError):
            ProcessOptions(group_by="invalid")


class TestProcessRequest:
    """Tests for ProcessRequest schema."""

    def test_creates_with_defaults(self):
        """Test creating request with default values."""
        request = ProcessRequest(upload_id="upload-123")

        assert request.upload_id == "upload-123"
        assert request.output_format == "xlsx"
        assert request.options.include_summary is True

    def test_creates_with_custom_format(self):
        """Test creating request with custom format."""
        request = ProcessRequest(upload_id="upload-123", output_format="pdf")

        assert request.output_format == "pdf"

    def test_output_format_validation(self):
        """Test output_format only accepts valid values."""
        ProcessRequest(upload_id="id", output_format="xlsx")
        ProcessRequest(upload_id="id", output_format="csv")
        ProcessRequest(upload_id="id", output_format="pdf")
        ProcessRequest(upload_id="id", output_format="json")

        with pytest.raises(ValidationError):
            ProcessRequest(upload_id="id", output_format="txt")


class TestProcessData:
    """Tests for ProcessData schema."""

    def test_creates_valid_data(self):
        """Test creating valid ProcessData."""
        now = datetime.utcnow()
        data = ProcessData(
            job_id="job-123",
            status="pending",
            estimated_time=30,
            created_at=now,
        )

        assert data.job_id == "job-123"
        assert data.status == "pending"
        assert data.estimated_time == 30


class TestProcessResponse:
    """Tests for ProcessResponse schema."""

    def test_creates_valid_response(self):
        """Test creating valid ProcessResponse."""
        now = datetime.utcnow()
        response = ProcessResponse(
            success=True,
            message="Processing started",
            data=ProcessData(
                job_id="job-123",
                status="pending",
                estimated_time=30,
                created_at=now,
            ),
        )

        assert response.success is True


class TestJobResult:
    """Tests for JobResult schema."""

    def test_creates_valid_result(self):
        """Test creating valid JobResult."""
        result = JobResult(
            total_invoices=10,
            total_amount=1500.50,
            output_file="result.xlsx",
        )

        assert result.total_invoices == 10
        assert result.total_amount == 1500.50
        assert result.output_file == "result.xlsx"
        assert result.output_path is None

    def test_with_output_path(self):
        """Test creating with optional output_path."""
        result = JobResult(
            total_invoices=5,
            total_amount=500.00,
            output_file="result.xlsx",
            output_path="/path/to/result.xlsx",
        )

        assert result.output_path == "/path/to/result.xlsx"


class TestJobData:
    """Tests for JobData schema."""

    def test_creates_pending_job(self):
        """Test creating pending job data."""
        data = JobData(job_id="job-123", status="pending")

        assert data.job_id == "job-123"
        assert data.status == "pending"
        assert data.progress == 0
        assert data.current_step is None
        assert data.result is None
        assert data.error is None

    def test_creates_processing_job(self):
        """Test creating processing job data."""
        now = datetime.utcnow()
        data = JobData(
            job_id="job-123",
            status="processing",
            progress=50,
            current_step="Processing invoices...",
            started_at=now,
        )

        assert data.progress == 50
        assert data.current_step == "Processing invoices..."
        assert data.started_at == now

    def test_creates_completed_job(self):
        """Test creating completed job data."""
        now = datetime.utcnow()
        data = JobData(
            job_id="job-123",
            status="completed",
            progress=100,
            result=JobResult(
                total_invoices=5,
                total_amount=1000.00,
                output_file="result.xlsx",
            ),
            completed_at=now,
        )

        assert data.status == "completed"
        assert data.result is not None
        assert data.result.total_invoices == 5

    def test_creates_failed_job(self):
        """Test creating failed job data."""
        now = datetime.utcnow()
        data = JobData(
            job_id="job-123",
            status="failed",
            error="Invalid file format",
            failed_at=now,
        )

        assert data.status == "failed"
        assert data.error == "Invalid file format"


class TestStatusResponse:
    """Tests for StatusResponse schema."""

    def test_creates_valid_response(self):
        """Test creating valid StatusResponse."""
        response = StatusResponse(
            success=True,
            data=JobData(job_id="job-123", status="pending"),
        )

        assert response.success is True
        assert response.data.job_id == "job-123"


class TestErrorResponse:
    """Tests for ErrorResponse schema."""

    def test_creates_valid_error(self):
        """Test creating valid ErrorResponse."""
        response = ErrorResponse(error="NOT_FOUND", message="Resource not found")

        assert response.success is False
        assert response.error == "NOT_FOUND"
        assert response.message == "Resource not found"

    def test_success_defaults_to_false(self):
        """Test success defaults to False."""
        response = ErrorResponse(error="ERROR", message="Error")

        assert response.success is False


class TestHealthResponse:
    """Tests for HealthResponse schema."""

    def test_creates_valid_response(self):
        """Test creating valid HealthResponse."""
        now = datetime.utcnow()
        response = HealthResponse(
            status="healthy",
            version="1.0.0",
            timestamp=now,
            services={"database": "ok", "storage": "ok"},
        )

        assert response.status == "healthy"
        assert response.version == "1.0.0"
        assert response.services["database"] == "ok"
