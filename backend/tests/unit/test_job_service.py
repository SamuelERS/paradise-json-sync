"""
JobService Tests / Pruebas del Servicio de Trabajos
====================================================

Unit tests for the JobService class.
Pruebas unitarias para la clase JobService.
"""

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pytest

from src.services.job_service import JobService, job_service
from src.models.invoice import Invoice, InvoiceItem, InvoiceType


class TestJobServiceInit:
    """Tests for JobService initialization."""

    def test_initialization(self):
        """Test that JobService initializes correctly."""
        service = JobService()
        assert service._jobs == {}

    def test_global_instance_exists(self):
        """Test that global job_service instance exists."""
        assert job_service is not None
        assert isinstance(job_service, JobService)


class TestCreateJob:
    """Tests for create_job method."""

    @pytest.fixture
    def service(self):
        """Fresh JobService instance for each test."""
        return JobService()

    @pytest.mark.asyncio
    async def test_create_job_basic(self, service):
        """Test creating a basic job."""
        job = await service.create_job(
            job_id="job-001",
            upload_id="upload-001",
            output_format="xlsx",
        )

        assert job["job_id"] == "job-001"
        assert job["upload_id"] == "upload-001"
        assert job["output_format"] == "xlsx"
        assert job["status"] == "pending"
        assert job["progress"] == 0
        assert job["options"] == {}

    @pytest.mark.asyncio
    async def test_create_job_with_options(self, service):
        """Test creating a job with options."""
        options = {"merge_pdfs": True, "include_summary": False}
        job = await service.create_job(
            job_id="job-002",
            upload_id="upload-002",
            output_format="pdf",
            options=options,
        )

        assert job["options"] == options

    @pytest.mark.asyncio
    async def test_create_job_sets_timestamps(self, service):
        """Test that created_at is set on job creation."""
        before = datetime.utcnow()
        job = await service.create_job(
            job_id="job-003",
            upload_id="upload-003",
            output_format="csv",
        )
        after = datetime.utcnow()

        assert job["created_at"] is not None
        assert before <= job["created_at"] <= after
        assert job["started_at"] is None
        assert job["completed_at"] is None
        assert job["failed_at"] is None

    @pytest.mark.asyncio
    async def test_create_job_stored_in_registry(self, service):
        """Test that created job is stored in _jobs registry."""
        await service.create_job(
            job_id="job-004",
            upload_id="upload-004",
            output_format="xlsx",
        )

        assert "job-004" in service._jobs
        assert service._jobs["job-004"]["upload_id"] == "upload-004"

    @pytest.mark.asyncio
    async def test_create_multiple_jobs(self, service):
        """Test creating multiple jobs."""
        await service.create_job("job-a", "upload-a", "xlsx")
        await service.create_job("job-b", "upload-b", "csv")
        await service.create_job("job-c", "upload-c", "pdf")

        assert len(service._jobs) == 3


class TestGetJob:
    """Tests for get_job method."""

    @pytest.fixture
    def service(self):
        """Fresh JobService instance for each test."""
        return JobService()

    @pytest.mark.asyncio
    async def test_get_existing_job(self, service):
        """Test getting an existing job."""
        await service.create_job("job-001", "upload-001", "xlsx")
        job = await service.get_job("job-001")

        assert job is not None
        assert job["job_id"] == "job-001"

    @pytest.mark.asyncio
    async def test_get_nonexistent_job(self, service):
        """Test getting a nonexistent job returns None."""
        job = await service.get_job("nonexistent")
        assert job is None


class TestUpdateProgress:
    """Tests for update_progress method."""

    @pytest.fixture
    def service(self):
        """Fresh JobService instance for each test."""
        return JobService()

    @pytest.mark.asyncio
    async def test_update_progress_basic(self, service):
        """Test updating job progress."""
        await service.create_job("job-001", "upload-001", "xlsx")
        result = await service.update_progress("job-001", 50)

        assert result is True
        job = await service.get_job("job-001")
        assert job["progress"] == 50
        assert job["status"] == "processing"

    @pytest.mark.asyncio
    async def test_update_progress_with_step(self, service):
        """Test updating progress with step description."""
        await service.create_job("job-001", "upload-001", "xlsx")
        await service.update_progress("job-001", 30, "Procesando facturas...")

        job = await service.get_job("job-001")
        assert job["current_step"] == "Procesando facturas..."

    @pytest.mark.asyncio
    async def test_update_progress_sets_started_at(self, service):
        """Test that first progress update sets started_at."""
        await service.create_job("job-001", "upload-001", "xlsx")
        job = await service.get_job("job-001")
        assert job["started_at"] is None

        await service.update_progress("job-001", 10)

        job = await service.get_job("job-001")
        assert job["started_at"] is not None

    @pytest.mark.asyncio
    async def test_update_progress_clamps_values(self, service):
        """Test that progress is clamped between 0 and 100."""
        await service.create_job("job-001", "upload-001", "xlsx")

        await service.update_progress("job-001", -10)
        job = await service.get_job("job-001")
        assert job["progress"] == 0

        await service.update_progress("job-001", 150)
        job = await service.get_job("job-001")
        assert job["progress"] == 100

    @pytest.mark.asyncio
    async def test_update_progress_nonexistent_job(self, service):
        """Test updating progress on nonexistent job returns False."""
        result = await service.update_progress("nonexistent", 50)
        assert result is False


class TestCompleteJob:
    """Tests for complete_job method."""

    @pytest.fixture
    def service(self):
        """Fresh JobService instance for each test."""
        return JobService()

    @pytest.fixture
    def sample_invoices(self):
        """Sample invoices for testing."""
        return [
            Invoice(
                document_number="FAC-001",
                invoice_type=InvoiceType.FACTURA,
                issue_date="2025-02-04",
                customer_name="Cliente 1",
                subtotal=Decimal("100.00"),
                tax=Decimal("13.00"),
                total=Decimal("113.00"),
            ),
            Invoice(
                document_number="FAC-002",
                invoice_type=InvoiceType.FACTURA,
                issue_date="2025-02-04",
                customer_name="Cliente 2",
                subtotal=Decimal("200.00"),
                tax=Decimal("26.00"),
                total=Decimal("226.00"),
            ),
        ]

    @pytest.mark.asyncio
    async def test_complete_job_basic(self, service, sample_invoices):
        """Test completing a job."""
        await service.create_job("job-001", "upload-001", "xlsx")
        result = await service.complete_job(
            "job-001",
            output_path="/output/result.xlsx",
            invoices=sample_invoices,
        )

        assert result is True
        job = await service.get_job("job-001")
        assert job["status"] == "completed"
        assert job["progress"] == 100

    @pytest.mark.asyncio
    async def test_complete_job_sets_result(self, service, sample_invoices):
        """Test that complete_job sets result data."""
        await service.create_job("job-001", "upload-001", "xlsx")
        await service.complete_job(
            "job-001",
            output_path="/output/result.xlsx",
            invoices=sample_invoices,
        )

        job = await service.get_job("job-001")
        assert job["result"] is not None
        assert job["result"]["total_invoices"] == 2
        assert job["result"]["total_amount"] == 339.00  # 113 + 226
        assert job["result"]["output_file"] == "result.xlsx"

    @pytest.mark.asyncio
    async def test_complete_job_sets_completed_at(self, service, sample_invoices):
        """Test that complete_job sets completed_at timestamp."""
        await service.create_job("job-001", "upload-001", "xlsx")
        await service.complete_job(
            "job-001",
            output_path="/output/result.xlsx",
            invoices=sample_invoices,
        )

        job = await service.get_job("job-001")
        assert job["completed_at"] is not None
        assert job["current_step"] is None

    @pytest.mark.asyncio
    async def test_complete_job_nonexistent(self, service, sample_invoices):
        """Test completing a nonexistent job returns False."""
        result = await service.complete_job(
            "nonexistent",
            output_path="/output/result.xlsx",
            invoices=sample_invoices,
        )
        assert result is False


class TestFailJob:
    """Tests for fail_job method."""

    @pytest.fixture
    def service(self):
        """Fresh JobService instance for each test."""
        return JobService()

    @pytest.mark.asyncio
    async def test_fail_job_basic(self, service):
        """Test failing a job."""
        await service.create_job("job-001", "upload-001", "xlsx")
        result = await service.fail_job("job-001", "Error procesando archivo")

        assert result is True
        job = await service.get_job("job-001")
        assert job["status"] == "failed"
        assert job["error"] == "Error procesando archivo"

    @pytest.mark.asyncio
    async def test_fail_job_sets_failed_at(self, service):
        """Test that fail_job sets failed_at timestamp."""
        await service.create_job("job-001", "upload-001", "xlsx")
        await service.fail_job("job-001", "Error")

        job = await service.get_job("job-001")
        assert job["failed_at"] is not None

    @pytest.mark.asyncio
    async def test_fail_job_nonexistent(self, service):
        """Test failing a nonexistent job returns False."""
        result = await service.fail_job("nonexistent", "Error")
        assert result is False


class TestDeleteJob:
    """Tests for delete_job method."""

    @pytest.fixture
    def service(self):
        """Fresh JobService instance for each test."""
        return JobService()

    @pytest.mark.asyncio
    async def test_delete_job_basic(self, service):
        """Test deleting a job."""
        await service.create_job("job-001", "upload-001", "xlsx")
        assert "job-001" in service._jobs

        result = await service.delete_job("job-001")

        assert result is True
        assert "job-001" not in service._jobs

    @pytest.mark.asyncio
    async def test_delete_job_nonexistent(self, service):
        """Test deleting a nonexistent job returns False."""
        result = await service.delete_job("nonexistent")
        assert result is False


class TestListJobs:
    """Tests for list_jobs method."""

    @pytest.fixture
    def service(self):
        """Fresh JobService instance for each test."""
        return JobService()

    @pytest.mark.asyncio
    async def test_list_jobs_empty(self, service):
        """Test listing jobs when none exist."""
        jobs = await service.list_jobs()
        assert jobs == []

    @pytest.mark.asyncio
    async def test_list_jobs_all(self, service):
        """Test listing all jobs."""
        await service.create_job("job-001", "upload-001", "xlsx")
        await service.create_job("job-002", "upload-002", "csv")

        jobs = await service.list_jobs()
        assert len(jobs) == 2

    @pytest.mark.asyncio
    async def test_list_jobs_by_status(self, service):
        """Test listing jobs filtered by status."""
        await service.create_job("job-001", "upload-001", "xlsx")
        await service.create_job("job-002", "upload-002", "csv")
        await service.update_progress("job-002", 50)  # Changes to "processing"

        pending_jobs = await service.list_jobs(status="pending")
        assert len(pending_jobs) == 1
        assert pending_jobs[0]["job_id"] == "job-001"

        processing_jobs = await service.list_jobs(status="processing")
        assert len(processing_jobs) == 1
        assert processing_jobs[0]["job_id"] == "job-002"

    @pytest.mark.asyncio
    async def test_list_jobs_no_match(self, service):
        """Test listing jobs with no status match."""
        await service.create_job("job-001", "upload-001", "xlsx")

        completed_jobs = await service.list_jobs(status="completed")
        assert completed_jobs == []


class TestJobLifecycle:
    """Integration tests for complete job lifecycle."""

    @pytest.fixture
    def service(self):
        """Fresh JobService instance for each test."""
        return JobService()

    @pytest.fixture
    def sample_invoices(self):
        """Sample invoices for testing."""
        return [
            Invoice(
                document_number="FAC-001",
                invoice_type=InvoiceType.FACTURA,
                issue_date="2025-02-04",
                customer_name="Cliente",
                subtotal=Decimal("100.00"),
                tax=Decimal("13.00"),
                total=Decimal("113.00"),
            ),
        ]

    @pytest.mark.asyncio
    async def test_successful_job_lifecycle(self, service, sample_invoices):
        """Test complete successful job lifecycle."""
        # 1. Create job
        job = await service.create_job("job-001", "upload-001", "xlsx")
        assert job["status"] == "pending"

        # 2. Start processing
        await service.update_progress("job-001", 10, "Iniciando...")
        job = await service.get_job("job-001")
        assert job["status"] == "processing"
        assert job["started_at"] is not None

        # 3. Progress updates
        await service.update_progress("job-001", 50, "Procesando facturas...")
        await service.update_progress("job-001", 90, "Generando reporte...")

        # 4. Complete
        await service.complete_job(
            "job-001",
            output_path="/output/result.xlsx",
            invoices=sample_invoices,
        )
        job = await service.get_job("job-001")
        assert job["status"] == "completed"
        assert job["completed_at"] is not None
        assert job["result"]["total_invoices"] == 1

    @pytest.mark.asyncio
    async def test_failed_job_lifecycle(self, service):
        """Test job lifecycle with failure."""
        # 1. Create job
        job = await service.create_job("job-001", "upload-001", "xlsx")
        assert job["status"] == "pending"

        # 2. Start processing
        await service.update_progress("job-001", 10, "Iniciando...")

        # 3. Failure occurs
        await service.fail_job("job-001", "Archivo corrupto detectado")

        job = await service.get_job("job-001")
        assert job["status"] == "failed"
        assert job["error"] == "Archivo corrupto detectado"
        assert job["failed_at"] is not None

    @pytest.mark.asyncio
    async def test_concurrent_jobs(self, service, sample_invoices):
        """Test handling multiple concurrent jobs."""
        # Create multiple jobs
        await service.create_job("job-a", "upload-a", "xlsx")
        await service.create_job("job-b", "upload-b", "csv")
        await service.create_job("job-c", "upload-c", "pdf")

        # Progress on different jobs
        await service.update_progress("job-a", 50)
        await service.update_progress("job-b", 30)

        # Complete one, fail another
        await service.complete_job("job-a", "/out/a.xlsx", sample_invoices)
        await service.fail_job("job-b", "Error")

        # Verify states
        assert (await service.get_job("job-a"))["status"] == "completed"
        assert (await service.get_job("job-b"))["status"] == "failed"
        assert (await service.get_job("job-c"))["status"] == "pending"

        # List by status
        assert len(await service.list_jobs(status="completed")) == 1
        assert len(await service.list_jobs(status="failed")) == 1
        assert len(await service.list_jobs(status="pending")) == 1
