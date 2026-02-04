"""
PDF Processor / Procesador de PDF
=================================

Process and merge PDF documents.
Procesa y une documentos PDF.

This module provides:
Este módulo provee:
- merge_pdfs: Merge multiple PDFs into one
              Une múltiples PDFs en uno
- validate_pdf: Validate that a file is a valid PDF
                Valida que un archivo sea un PDF válido
- get_page_count: Get the number of pages in a PDF
                  Obtiene el número de páginas en un PDF
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logger.warning("PyMuPDF not installed. PDF processing will be limited.")


class PDFProcessorError(Exception):
    """
    Custom exception for PDF processing errors.
    Excepción personalizada para errores de procesamiento PDF.
    """

    def __init__(
        self,
        message: str,
        file_path: str | None = None,
        original_error: Exception | None = None,
    ) -> None:
        self.message = message
        self.file_path = file_path
        self.original_error = original_error
        super().__init__(self.message)


class PDFProcessor:
    """
    PDF document processor / Procesador de documentos PDF.

    Handles PDF merging, validation, and page counting using PyMuPDF.
    Maneja unión, validación y conteo de páginas de PDF usando PyMuPDF.

    Attributes / Atributos:
        output_dir: Default directory for merged PDFs
                    Directorio por defecto para PDFs unidos
    """

    def __init__(self, output_dir: str | None = None) -> None:
        """
        Initialize the PDF processor.
        Inicializa el procesador PDF.

        Args / Argumentos:
            output_dir: Default output directory / Directorio de salida por defecto
        """
        if not PYMUPDF_AVAILABLE:
            logger.warning(
                "PyMuPDF not available. Install with: pip install PyMuPDF"
            )

        self.output_dir = Path(output_dir) if output_dir else None
        logger.debug("PDFProcessor initialized with output_dir=%s", output_dir)

    def merge_pdfs(
        self,
        pdf_paths: list[str],
        output_path: str,
    ) -> str:
        """
        Merge multiple PDF files into a single PDF.
        Une múltiples archivos PDF en un solo PDF.

        Args / Argumentos:
            pdf_paths: List of paths to PDF files to merge
                       Lista de rutas a archivos PDF para unir
            output_path: Path for the merged output PDF
                         Ruta para el PDF de salida unido

        Returns / Retorna:
            Path to the merged PDF file / Ruta al archivo PDF unido

        Raises / Lanza:
            PDFProcessorError: If merging fails / Si la unión falla
        """
        if not PYMUPDF_AVAILABLE:
            raise PDFProcessorError("PyMuPDF is not installed")

        if not pdf_paths:
            raise PDFProcessorError("No PDF files provided for merging")

        logger.info("Merging %d PDF files into %s", len(pdf_paths), output_path)

        # Validate all input files first
        valid_paths = []
        for pdf_path in pdf_paths:
            if self.validate_pdf(pdf_path):
                valid_paths.append(pdf_path)
            else:
                logger.warning("Skipping invalid PDF: %s", pdf_path)

        if not valid_paths:
            raise PDFProcessorError("No valid PDF files to merge")

        try:
            merged_doc = fitz.open()

            for pdf_path in valid_paths:
                try:
                    doc = fitz.open(pdf_path)
                    merged_doc.insert_pdf(doc)
                    doc.close()
                    logger.debug("Added %s to merged document", pdf_path)
                except Exception as e:
                    logger.error("Error adding PDF %s: %s", pdf_path, e)
                    continue

            if merged_doc.page_count == 0:
                merged_doc.close()
                raise PDFProcessorError("Merged document has no pages")

            # Ensure output directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            merged_doc.save(str(output_file))
            merged_doc.close()

            logger.info(
                "Successfully merged %d PDFs into %s (%d pages)",
                len(valid_paths),
                output_path,
                self.get_page_count(output_path),
            )

            return str(output_file)

        except PDFProcessorError:
            raise
        except Exception as e:
            raise PDFProcessorError(
                f"Error merging PDFs: {e}",
                original_error=e,
            ) from e

    def validate_pdf(self, pdf_path: str) -> bool:
        """
        Validate that a file is a valid PDF.
        Valida que un archivo sea un PDF válido.

        Args / Argumentos:
            pdf_path: Path to the PDF file / Ruta al archivo PDF

        Returns / Retorna:
            True if valid PDF / True si es un PDF válido
        """
        path = Path(pdf_path)

        # Check file exists
        if not path.exists():
            logger.warning("PDF file does not exist: %s", pdf_path)
            return False

        # Check extension
        if path.suffix.lower() != ".pdf":
            logger.warning("File does not have .pdf extension: %s", pdf_path)
            return False

        # Check file size
        if path.stat().st_size == 0:
            logger.warning("PDF file is empty: %s", pdf_path)
            return False

        if not PYMUPDF_AVAILABLE:
            logger.warning("Cannot fully validate PDF without PyMuPDF")
            return True

        # Try to open with PyMuPDF
        try:
            doc = fitz.open(pdf_path)
            is_valid = doc.is_pdf
            page_count = doc.page_count
            doc.close()

            if not is_valid:
                logger.warning("File is not a valid PDF: %s", pdf_path)
                return False

            if page_count == 0:
                logger.warning("PDF has no pages: %s", pdf_path)
                return False

            logger.debug("PDF validated: %s (%d pages)", pdf_path, page_count)
            return True

        except Exception as e:
            logger.warning("Error validating PDF %s: %s", pdf_path, e)
            return False

    def get_page_count(self, pdf_path: str) -> int:
        """
        Get the number of pages in a PDF file.
        Obtiene el número de páginas en un archivo PDF.

        Args / Argumentos:
            pdf_path: Path to the PDF file / Ruta al archivo PDF

        Returns / Retorna:
            Number of pages / Número de páginas

        Raises / Lanza:
            PDFProcessorError: If page count cannot be determined
                               Si el conteo de páginas no puede determinarse
        """
        if not PYMUPDF_AVAILABLE:
            raise PDFProcessorError("PyMuPDF is not installed")

        path = Path(pdf_path)

        if not path.exists():
            raise PDFProcessorError(
                f"PDF file does not exist: {pdf_path}",
                file_path=pdf_path,
            )

        try:
            doc = fitz.open(pdf_path)
            page_count = doc.page_count
            doc.close()

            logger.debug("PDF %s has %d pages", pdf_path, page_count)
            return page_count

        except Exception as e:
            raise PDFProcessorError(
                f"Error getting page count: {e}",
                file_path=pdf_path,
                original_error=e,
            ) from e

    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file.
        Extrae contenido de texto de un archivo PDF.

        Args / Argumentos:
            pdf_path: Path to the PDF file / Ruta al archivo PDF

        Returns / Retorna:
            Extracted text content / Contenido de texto extraído

        Raises / Lanza:
            PDFProcessorError: If text extraction fails
                               Si la extracción de texto falla
        """
        if not PYMUPDF_AVAILABLE:
            raise PDFProcessorError("PyMuPDF is not installed")

        if not self.validate_pdf(pdf_path):
            raise PDFProcessorError(
                "Invalid PDF file",
                file_path=pdf_path,
            )

        try:
            doc = fitz.open(pdf_path)
            text_content = []

            for page in doc:
                text_content.append(page.get_text())

            doc.close()

            full_text = "\n".join(text_content)
            logger.debug(
                "Extracted %d characters from %s",
                len(full_text),
                pdf_path,
            )

            return full_text

        except Exception as e:
            raise PDFProcessorError(
                f"Error extracting text: {e}",
                file_path=pdf_path,
                original_error=e,
            ) from e

    def split_pdf(
        self,
        pdf_path: str,
        output_dir: str,
        prefix: str = "page",
    ) -> list[str]:
        """
        Split a PDF into individual page files.
        Divide un PDF en archivos individuales por página.

        Args / Argumentos:
            pdf_path: Path to the PDF file / Ruta al archivo PDF
            output_dir: Directory for output files / Directorio para archivos de salida
            prefix: Prefix for output filenames / Prefijo para nombres de archivo

        Returns / Retorna:
            List of paths to individual page PDFs
            Lista de rutas a PDFs individuales por página

        Raises / Lanza:
            PDFProcessorError: If splitting fails / Si la división falla
        """
        if not PYMUPDF_AVAILABLE:
            raise PDFProcessorError("PyMuPDF is not installed")

        if not self.validate_pdf(pdf_path):
            raise PDFProcessorError(
                "Invalid PDF file",
                file_path=pdf_path,
            )

        try:
            doc = fitz.open(pdf_path)
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            output_files: list[str] = []

            for i, _page in enumerate(doc):
                page_doc = fitz.open()
                page_doc.insert_pdf(doc, from_page=i, to_page=i)

                page_file = output_path / f"{prefix}_{i + 1:03d}.pdf"
                page_doc.save(str(page_file))
                page_doc.close()

                output_files.append(str(page_file))

            doc.close()

            logger.info(
                "Split %s into %d page files in %s",
                pdf_path,
                len(output_files),
                output_dir,
            )

            return output_files

        except PDFProcessorError:
            raise
        except Exception as e:
            raise PDFProcessorError(
                f"Error splitting PDF: {e}",
                file_path=pdf_path,
                original_error=e,
            ) from e
