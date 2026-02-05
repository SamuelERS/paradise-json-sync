"""
FileService Tests / Pruebas del Servicio de Archivos
====================================================

Unit tests for the FileService class.
Pruebas unitarias para la clase FileService.
"""

import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from src.services.file_service import FileService, file_service


class TestFileServiceInit:
    """Tests for FileService initialization."""

    def test_initialization_default_directory(self, tmp_path):
        """Test that FileService initializes with default directory."""
        with patch("src.services.file_service.UPLOAD_DIR", tmp_path / "uploads"):
            service = FileService()
            assert service.upload_dir.exists()
            assert service._uploads == {}

    def test_initialization_custom_directory(self, tmp_path):
        """Test that FileService initializes with custom directory."""
        custom_dir = tmp_path / "custom_uploads"
        service = FileService(upload_dir=custom_dir)

        assert service.upload_dir == custom_dir
        assert custom_dir.exists()

    def test_initialization_creates_directory(self, tmp_path):
        """Test that FileService creates upload directory if not exists."""
        custom_dir = tmp_path / "new_dir" / "uploads"
        assert not custom_dir.exists()

        service = FileService(upload_dir=custom_dir)
        assert custom_dir.exists()

    def test_global_instance_exists(self):
        """Test that global file_service instance exists."""
        assert file_service is not None
        assert isinstance(file_service, FileService)


class TestSaveUpload:
    """Tests for save_upload method."""

    @pytest.fixture
    def service(self, tmp_path):
        """Fresh FileService instance for each test."""
        return FileService(upload_dir=tmp_path / "uploads")

    @pytest.fixture
    def sample_files(self):
        """Sample file data for testing."""
        return [
            {
                "name": "invoice1.json",
                "content": b'{"document_number": "FAC-001"}',
                "size": 30,
                "type": "application/json",
            },
            {
                "name": "invoice2.json",
                "content": b'{"document_number": "FAC-002"}',
                "size": 30,
                "type": "application/json",
            },
        ]

    @pytest.mark.asyncio
    async def test_save_upload_basic(self, service, sample_files):
        """Test saving uploaded files."""
        saved = await service.save_upload("upload-001", sample_files)

        assert len(saved) == 2
        assert saved[0]["name"] == "invoice1.json"
        assert saved[1]["name"] == "invoice2.json"

    @pytest.mark.asyncio
    async def test_save_upload_creates_directory(self, service, sample_files):
        """Test that save_upload creates upload directory."""
        await service.save_upload("upload-001", sample_files)

        upload_path = service.upload_dir / "upload-001"
        assert upload_path.exists()

    @pytest.mark.asyncio
    async def test_save_upload_writes_files(self, service, sample_files):
        """Test that files are written to disk."""
        await service.save_upload("upload-001", sample_files)

        file1_path = service.upload_dir / "upload-001" / "invoice1.json"
        file2_path = service.upload_dir / "upload-001" / "invoice2.json"

        assert file1_path.exists()
        assert file2_path.exists()

        with open(file1_path, "rb") as f:
            assert b"FAC-001" in f.read()

    @pytest.mark.asyncio
    async def test_save_upload_registers_upload(self, service, sample_files):
        """Test that upload is registered in _uploads."""
        await service.save_upload("upload-001", sample_files)

        assert "upload-001" in service._uploads
        upload = service._uploads["upload-001"]
        assert upload["total_files"] == 2
        assert "created_at" in upload
        assert "expires_at" in upload

    @pytest.mark.asyncio
    async def test_save_upload_sets_expiration(self, service, sample_files):
        """Test that expiration is set 24 hours in future."""
        before = datetime.utcnow()
        await service.save_upload("upload-001", sample_files)
        after = datetime.utcnow()

        upload = service._uploads["upload-001"]
        expected_min = before + timedelta(hours=24)
        expected_max = after + timedelta(hours=24)

        assert expected_min <= upload["expires_at"] <= expected_max

    @pytest.mark.asyncio
    async def test_save_upload_returns_file_info(self, service, sample_files):
        """Test that returned file info contains correct data."""
        saved = await service.save_upload("upload-001", sample_files)

        assert saved[0]["name"] == "invoice1.json"
        assert saved[0]["size"] == 30
        assert saved[0]["type"] == "application/json"
        assert "path" in saved[0]

    @pytest.mark.asyncio
    async def test_save_upload_empty_list(self, service):
        """Test saving empty file list."""
        saved = await service.save_upload("upload-001", [])

        assert saved == []
        assert service._uploads["upload-001"]["total_files"] == 0


class TestGetUpload:
    """Tests for get_upload method."""

    @pytest.fixture
    def service(self, tmp_path):
        """Fresh FileService instance for each test."""
        return FileService(upload_dir=tmp_path / "uploads")

    @pytest.fixture
    def sample_files(self):
        """Sample file data for testing."""
        return [
            {
                "name": "test.json",
                "content": b"{}",
                "size": 2,
                "type": "application/json",
            },
        ]

    @pytest.mark.asyncio
    async def test_get_existing_upload(self, service, sample_files):
        """Test getting an existing upload."""
        await service.save_upload("upload-001", sample_files)
        upload = await service.get_upload("upload-001")

        assert upload is not None
        assert upload["total_files"] == 1

    @pytest.mark.asyncio
    async def test_get_nonexistent_upload(self, service):
        """Test getting a nonexistent upload returns None."""
        upload = await service.get_upload("nonexistent")
        assert upload is None


class TestGetFiles:
    """Tests for get_files method."""

    @pytest.fixture
    def service(self, tmp_path):
        """Fresh FileService instance for each test."""
        return FileService(upload_dir=tmp_path / "uploads")

    @pytest.fixture
    def sample_files(self):
        """Sample file data for testing."""
        return [
            {
                "name": "file1.json",
                "content": b"{}",
                "size": 2,
                "type": "application/json",
            },
            {
                "name": "file2.pdf",
                "content": b"%PDF",
                "size": 4,
                "type": "application/pdf",
            },
        ]

    @pytest.mark.asyncio
    async def test_get_files_existing_upload(self, service, sample_files):
        """Test getting files from existing upload."""
        await service.save_upload("upload-001", sample_files)
        files = await service.get_files("upload-001")

        assert len(files) == 2
        assert files[0]["name"] == "file1.json"
        assert files[1]["name"] == "file2.pdf"

    @pytest.mark.asyncio
    async def test_get_files_nonexistent_upload(self, service):
        """Test getting files from nonexistent upload returns empty list."""
        files = await service.get_files("nonexistent")
        assert files == []


class TestDeleteUpload:
    """Tests for delete_upload method."""

    @pytest.fixture
    def service(self, tmp_path):
        """Fresh FileService instance for each test."""
        return FileService(upload_dir=tmp_path / "uploads")

    @pytest.fixture
    def sample_files(self):
        """Sample file data for testing."""
        return [
            {
                "name": "test.json",
                "content": b"{}",
                "size": 2,
                "type": "application/json",
            },
        ]

    @pytest.mark.asyncio
    async def test_delete_upload_basic(self, service, sample_files):
        """Test deleting an upload."""
        await service.save_upload("upload-001", sample_files)
        assert "upload-001" in service._uploads

        result = await service.delete_upload("upload-001")

        assert result is True
        assert "upload-001" not in service._uploads

    @pytest.mark.asyncio
    async def test_delete_upload_removes_files(self, service, sample_files):
        """Test that delete_upload removes files from disk."""
        await service.save_upload("upload-001", sample_files)
        upload_path = service.upload_dir / "upload-001"
        assert upload_path.exists()

        await service.delete_upload("upload-001")

        assert not upload_path.exists()

    @pytest.mark.asyncio
    async def test_delete_upload_nonexistent(self, service):
        """Test deleting nonexistent upload returns False."""
        result = await service.delete_upload("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_upload_missing_directory(self, service, sample_files):
        """Test delete_upload when directory already removed."""
        await service.save_upload("upload-001", sample_files)

        # Manually remove directory
        upload_path = service.upload_dir / "upload-001"
        shutil.rmtree(upload_path)

        # Should still work (removing from registry)
        result = await service.delete_upload("upload-001")
        assert result is True
        assert "upload-001" not in service._uploads


class TestCleanupExpired:
    """Tests for cleanup_expired method."""

    @pytest.fixture
    def service(self, tmp_path):
        """Fresh FileService instance for each test."""
        return FileService(upload_dir=tmp_path / "uploads")

    @pytest.fixture
    def sample_files(self):
        """Sample file data for testing."""
        return [
            {
                "name": "test.json",
                "content": b"{}",
                "size": 2,
                "type": "application/json",
            },
        ]

    @pytest.mark.asyncio
    async def test_cleanup_no_expired(self, service, sample_files):
        """Test cleanup when no uploads are expired."""
        await service.save_upload("upload-001", sample_files)

        cleaned = await service.cleanup_expired()

        assert cleaned == 0
        assert "upload-001" in service._uploads

    @pytest.mark.asyncio
    async def test_cleanup_expired_uploads(self, service, sample_files):
        """Test cleanup removes expired uploads."""
        await service.save_upload("upload-001", sample_files)
        await service.save_upload("upload-002", sample_files)

        # Manually expire upload-001
        service._uploads["upload-001"]["expires_at"] = datetime.utcnow() - timedelta(hours=1)

        cleaned = await service.cleanup_expired()

        assert cleaned == 1
        assert "upload-001" not in service._uploads
        assert "upload-002" in service._uploads

    @pytest.mark.asyncio
    async def test_cleanup_removes_files(self, service, sample_files):
        """Test that cleanup removes files from disk."""
        await service.save_upload("upload-001", sample_files)
        upload_path = service.upload_dir / "upload-001"
        assert upload_path.exists()

        # Expire upload
        service._uploads["upload-001"]["expires_at"] = datetime.utcnow() - timedelta(hours=1)

        await service.cleanup_expired()

        assert not upload_path.exists()

    @pytest.mark.asyncio
    async def test_cleanup_multiple_expired(self, service, sample_files):
        """Test cleanup handles multiple expired uploads."""
        for i in range(5):
            await service.save_upload(f"upload-{i:03d}", sample_files)
            if i < 3:  # Expire first 3
                service._uploads[f"upload-{i:03d}"]["expires_at"] = datetime.utcnow() - timedelta(hours=1)

        cleaned = await service.cleanup_expired()

        assert cleaned == 3
        assert len(service._uploads) == 2


class TestFileServiceIntegration:
    """Integration tests for FileService workflows."""

    @pytest.fixture
    def service(self, tmp_path):
        """Fresh FileService instance for each test."""
        return FileService(upload_dir=tmp_path / "uploads")

    @pytest.mark.asyncio
    async def test_full_upload_lifecycle(self, service):
        """Test complete upload lifecycle."""
        files = [
            {
                "name": "invoice.json",
                "content": b'{"document_number": "FAC-001", "total": 100.00}',
                "size": 45,
                "type": "application/json",
            },
        ]

        # 1. Save upload
        saved = await service.save_upload("upload-001", files)
        assert len(saved) == 1

        # 2. Verify upload exists
        upload = await service.get_upload("upload-001")
        assert upload is not None

        # 3. Get files
        retrieved_files = await service.get_files("upload-001")
        assert len(retrieved_files) == 1

        # 4. Read file content
        file_path = Path(retrieved_files[0]["path"])
        assert file_path.exists()
        with open(file_path, "rb") as f:
            content = f.read()
            assert b"FAC-001" in content

        # 5. Delete upload
        result = await service.delete_upload("upload-001")
        assert result is True
        assert not file_path.exists()

    @pytest.mark.asyncio
    async def test_multiple_uploads_isolation(self, service):
        """Test that multiple uploads are isolated."""
        files1 = [
            {
                "name": "a.json",
                "content": b'{"id": "A"}',
                "size": 12,
                "type": "application/json",
            },
        ]
        files2 = [
            {
                "name": "b.json",
                "content": b'{"id": "B"}',
                "size": 12,
                "type": "application/json",
            },
        ]

        await service.save_upload("upload-a", files1)
        await service.save_upload("upload-b", files2)

        # Verify isolation
        files_a = await service.get_files("upload-a")
        files_b = await service.get_files("upload-b")

        assert files_a[0]["name"] == "a.json"
        assert files_b[0]["name"] == "b.json"

        # Delete one shouldn't affect other
        await service.delete_upload("upload-a")

        assert await service.get_upload("upload-a") is None
        assert await service.get_upload("upload-b") is not None

    @pytest.mark.asyncio
    async def test_special_characters_in_filename(self, service):
        """Test handling files with special characters in name."""
        files = [
            {
                "name": "factura (1).json",
                "content": b"{}",
                "size": 2,
                "type": "application/json",
            },
            {
                "name": "documento-2025_01.pdf",
                "content": b"%PDF",
                "size": 4,
                "type": "application/pdf",
            },
        ]

        saved = await service.save_upload("upload-001", files)

        assert len(saved) == 2

        # Verify files exist
        for file_info in saved:
            path = Path(file_info["path"])
            assert path.exists()
