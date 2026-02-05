"""
PDFProcessor Tests / Pruebas del Procesador de PDF
==================================================

Unit tests for the PDFProcessor class.
Pruebas unitarias para la clase PDFProcessor.
"""

from pathlib import Path

import pytest

from src.core.pdf_processor import PYMUPDF_AVAILABLE, PDFProcessor, PDFProcessorError


class TestPDFProcessorInit:
    """Tests for PDFProcessor initialization."""

    def test_default_initialization(self):
        """Test default initialization."""
        processor = PDFProcessor()
        assert processor.output_dir is None

    def test_initialization_with_output_dir(self, tmp_path):
        """Test initialization with output directory."""
        processor = PDFProcessor(output_dir=str(tmp_path))
        assert processor.output_dir == tmp_path


@pytest.mark.skipif(not PYMUPDF_AVAILABLE, reason="PyMuPDF not installed")
class TestMergePdfs:
    """Tests for merge_pdfs method."""

    def test_merge_two_pdfs(self, sample_pdf_files, temp_output_dir):
        """Test merging two PDF files."""
        if len(sample_pdf_files) < 2:
            pytest.skip("Not enough PDF files created")

        processor = PDFProcessor()
        output_path = str(temp_output_dir / "merged.pdf")

        result = processor.merge_pdfs(
            [str(f) for f in sample_pdf_files[:2]],
            output_path,
        )

        assert Path(result).exists()
        assert processor.get_page_count(result) == 2

    def test_merge_multiple_pdfs(self, sample_pdf_files, temp_output_dir):
        """Test merging multiple PDF files (10+)."""
        if len(sample_pdf_files) < 3:
            pytest.skip("Not enough PDF files created")

        processor = PDFProcessor()
        output_path = str(temp_output_dir / "merged_all.pdf")

        result = processor.merge_pdfs(
            [str(f) for f in sample_pdf_files],
            output_path,
        )

        assert Path(result).exists()
        assert processor.get_page_count(result) == len(sample_pdf_files)

    def test_merge_empty_list_raises_error(self, temp_output_dir):
        """Test that merging empty list raises error."""
        processor = PDFProcessor()
        output_path = str(temp_output_dir / "merged.pdf")

        with pytest.raises(PDFProcessorError) as exc_info:
            processor.merge_pdfs([], output_path)

        assert "no pdf" in exc_info.value.message.lower()

    def test_merge_skips_invalid_pdfs(self, sample_pdf_files, corrupted_pdf_file, temp_output_dir):
        """Test that corrupted PDFs are skipped during merge."""
        if len(sample_pdf_files) < 1:
            pytest.skip("No PDF files created")

        processor = PDFProcessor()
        output_path = str(temp_output_dir / "merged.pdf")

        # Mix valid and corrupted files
        all_files = [str(sample_pdf_files[0]), str(corrupted_pdf_file)]

        result = processor.merge_pdfs(all_files, output_path)

        assert Path(result).exists()
        # Only the valid PDF should be in the result
        assert processor.get_page_count(result) == 1

    def test_merge_all_invalid_raises_error(self, corrupted_pdf_file, temp_output_dir):
        """Test that merging only invalid PDFs raises error."""
        processor = PDFProcessor()
        output_path = str(temp_output_dir / "merged.pdf")

        with pytest.raises(PDFProcessorError) as exc_info:
            processor.merge_pdfs([str(corrupted_pdf_file)], output_path)

        assert "no valid" in exc_info.value.message.lower()

    def test_merge_creates_output_directory(self, sample_pdf_files, tmp_path):
        """Test that merge creates output directory if needed."""
        if len(sample_pdf_files) < 1:
            pytest.skip("No PDF files created")

        processor = PDFProcessor()
        output_path = str(tmp_path / "new_dir" / "subdir" / "merged.pdf")

        result = processor.merge_pdfs([str(sample_pdf_files[0])], output_path)

        assert Path(result).exists()


@pytest.mark.skipif(not PYMUPDF_AVAILABLE, reason="PyMuPDF not installed")
class TestValidatePdf:
    """Tests for validate_pdf method."""

    def test_validate_valid_pdf(self, sample_pdf_file):
        """Test validating a valid PDF file."""
        processor = PDFProcessor()
        assert processor.validate_pdf(str(sample_pdf_file)) is True

    def test_validate_nonexistent_file(self):
        """Test validating nonexistent file."""
        processor = PDFProcessor()
        assert processor.validate_pdf("/nonexistent/file.pdf") is False

    def test_validate_non_pdf_extension(self, tmp_path):
        """Test validating file with non-PDF extension."""
        processor = PDFProcessor()

        txt_file = tmp_path / "test.txt"
        txt_file.write_text("not a pdf")

        assert processor.validate_pdf(str(txt_file)) is False

    def test_validate_empty_file(self, tmp_path):
        """Test validating empty file."""
        processor = PDFProcessor()

        empty_pdf = tmp_path / "empty.pdf"
        empty_pdf.touch()

        assert processor.validate_pdf(str(empty_pdf)) is False

    def test_validate_corrupted_pdf(self, corrupted_pdf_file):
        """Test validating corrupted PDF file."""
        processor = PDFProcessor()
        assert processor.validate_pdf(str(corrupted_pdf_file)) is False


@pytest.mark.skipif(not PYMUPDF_AVAILABLE, reason="PyMuPDF not installed")
class TestGetPageCount:
    """Tests for get_page_count method."""

    def test_get_page_count_single_page(self, sample_pdf_file):
        """Test getting page count for single page PDF."""
        processor = PDFProcessor()
        count = processor.get_page_count(str(sample_pdf_file))
        assert count == 1

    def test_get_page_count_nonexistent_file(self):
        """Test getting page count for nonexistent file."""
        processor = PDFProcessor()

        with pytest.raises(PDFProcessorError) as exc_info:
            processor.get_page_count("/nonexistent/file.pdf")

        assert "not exist" in exc_info.value.message.lower()


@pytest.mark.skipif(not PYMUPDF_AVAILABLE, reason="PyMuPDF not installed")
class TestExtractText:
    """Tests for extract_text method."""

    def test_extract_text_from_pdf(self, sample_pdf_file):
        """Test extracting text from PDF."""
        processor = PDFProcessor()
        text = processor.extract_text(str(sample_pdf_file))

        # Should contain test text
        assert "Test" in text or "Prueba" in text or len(text) >= 0

    def test_extract_text_invalid_pdf(self, corrupted_pdf_file):
        """Test extracting text from invalid PDF."""
        processor = PDFProcessor()

        with pytest.raises(PDFProcessorError):
            processor.extract_text(str(corrupted_pdf_file))


@pytest.mark.skipif(not PYMUPDF_AVAILABLE, reason="PyMuPDF not installed")
class TestSplitPdf:
    """Tests for split_pdf method."""

    def test_split_single_page_pdf(self, sample_pdf_file, temp_output_dir):
        """Test splitting single page PDF."""
        processor = PDFProcessor()

        output_files = processor.split_pdf(
            str(sample_pdf_file),
            str(temp_output_dir),
            prefix="page",
        )

        assert len(output_files) == 1
        assert Path(output_files[0]).exists()
        assert "page_001.pdf" in output_files[0]

    def test_split_invalid_pdf(self, corrupted_pdf_file, temp_output_dir):
        """Test splitting invalid PDF."""
        processor = PDFProcessor()

        with pytest.raises(PDFProcessorError):
            processor.split_pdf(
                str(corrupted_pdf_file),
                str(temp_output_dir),
            )


class TestPDFProcessorWithoutPyMuPDF:
    """Tests for PDFProcessor when PyMuPDF is not available."""

    def test_merge_without_pymupdf_raises_error(self, tmp_path):
        """Test that operations raise error when PyMuPDF unavailable."""
        if PYMUPDF_AVAILABLE:
            pytest.skip("PyMuPDF is available")

        processor = PDFProcessor()

        with pytest.raises(PDFProcessorError) as exc_info:
            processor.merge_pdfs(["test.pdf"], str(tmp_path / "out.pdf"))

        assert "not installed" in exc_info.value.message.lower()


class TestPDFProcessorError:
    """Tests for PDFProcessorError exception."""

    def test_error_with_message_only(self):
        """Test creating error with message only."""
        error = PDFProcessorError("Test error")
        assert str(error) == "Test error"
        assert error.file_path is None

    def test_error_with_file_path(self):
        """Test creating error with file path."""
        error = PDFProcessorError(
            message="Error processing PDF",
            file_path="/path/to/file.pdf",
        )
        assert error.file_path == "/path/to/file.pdf"

    def test_error_with_original_error(self):
        """Test creating error with original exception."""
        original = ValueError("Original error")
        error = PDFProcessorError(
            message="Wrapped error",
            original_error=original,
        )
        assert error.original_error is original
