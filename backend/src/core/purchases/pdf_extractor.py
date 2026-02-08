"""
PDF Extractor / Extractor de PDF
=================================

Extract structured data from digital PDF invoices using PyMuPDF + regex.
Extrae datos estructurados de facturas PDF digitales usando PyMuPDF + regex.

This module provides / Este modulo provee:
- PDFExtractionError: Exception for PDF extraction failures
                      Excepcion para fallos de extraccion de PDF
- PDFExtractor: Extract invoice data from digital PDFs (selectable text)
                Extrae datos de facturas de PDFs digitales (texto seleccionable)

Phase 1: Digital PDFs only (selectable text). No OCR.
Fase 1: Solo PDFs digitales (texto seleccionable). Sin OCR.
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

# Minimum text length to consider a PDF as having extractable text
# Longitud minima de texto para considerar un PDF con texto extraible
_MIN_TEXT_LENGTH = 50


class PDFExtractionError(Exception):
    """
    Error during PDF data extraction.
    Error durante la extraccion de datos de PDF.

    Attributes / Atributos:
        message: Error description / Descripcion del error
        file_path: Source file path / Ruta del archivo fuente
        partial_data: Partially extracted data / Datos parciales extraidos
    """

    def __init__(
        self,
        message: str,
        file_path: str = "",
        partial_data: Optional[dict] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.file_path = file_path
        self.partial_data = partial_data or {}


class PDFExtractor:
    """
    Extract structured data from digital PDF invoices.
    Extrae datos estructurados de facturas PDF digitales.

    Phase 1: Digital PDFs only (selectable text). No OCR.
    Fase 1: Solo PDFs digitales (texto seleccionable). Sin OCR.

    Uses PyMuPDF (fitz) for text extraction and regex patterns
    to identify common fields in El Salvador DTE invoices.
    Usa PyMuPDF (fitz) para extraccion de texto y patrones regex
    para identificar campos comunes en facturas DTE de El Salvador.
    """

    # Regex patterns for common invoice fields
    # Patrones regex para campos comunes en facturas
    PATTERNS: dict[str, list[str]] = {
        "control_number": [
            r"DTE-\d{2}-[A-Z0-9]+-[A-Z0-9]+",
            r"N[°ú]mero de Control[:\s]+([^\n]+)",
            r"No\.\s*Control[:\s]+([^\n]+)",
        ],
        "document_number": [
            r"C[óo]digo de Generaci[óo]n[:\s]+([A-F0-9-]+)",
            r"UUID[:\s]+([A-F0-9-]+)",
            r"[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}",
        ],
        "date": [
            r"Fecha de Emisi[óo]n[:\s]+(\d{2}/\d{2}/\d{4})",
            r"Fecha[:\s]+(\d{4}-\d{2}-\d{2})",
            r"Fecha[:\s]+(\d{2}-\d{2}-\d{4})",
        ],
        "supplier_name": [
            r"Emisor[:\s]+([^\n]+)",
            r"Raz[óo]n Social[:\s]+([^\n]+)",
            r"Nombre del Emisor[:\s]+([^\n]+)",
        ],
        "supplier_nit": [
            r"NIT[:\s]+(\d{4}-\d{6}-\d{3}-\d)",
            r"NIT del Emisor[:\s]+([^\n]+)",
        ],
        "supplier_nrc": [
            r"NRC[:\s]+(\d+-\d+)",
            r"NRC del Emisor[:\s]+([^\n]+)",
        ],
        "total": [
            r"Total a Pagar[:\s]+\$?([\d,]+\.\d{2})",
            r"TOTAL[:\s]+\$?([\d,]+\.\d{2})",
            r"Total Pagar[:\s]+\$?([\d,]+\.\d{2})",
        ],
        "iva": [
            r"IVA[:\s]+\$?([\d,]+\.\d{2})",
            r"Total IVA[:\s]+\$?([\d,]+\.\d{2})",
            r"Impuesto[:\s]+\$?([\d,]+\.\d{2})",
        ],
        "subtotal": [
            r"Sub\s?Total[:\s]+\$?([\d,]+\.\d{2})",
            r"SubTotal Ventas[:\s]+\$?([\d,]+\.\d{2})",
        ],
    }

    def extract(self, pdf_path: str) -> dict:
        """
        Extract data from a PDF invoice.
        Extrae datos de una factura PDF.

        Returns normalized dict compatible with mappers.
        Retorna dict normalizado compatible con mappers.

        Args / Argumentos:
            pdf_path: Path to the PDF file / Ruta al archivo PDF

        Returns / Retorna:
            Dict with extracted fields / Dict con campos extraidos

        Raises / Lanza:
            PDFExtractionError: If text unreadable or no total found
        """
        text = self._extract_text(pdf_path)

        if len(text.strip()) < _MIN_TEXT_LENGTH:
            raise PDFExtractionError(
                message="PDF sin texto extraible / PDF has no extractable text",
                file_path=pdf_path,
            )

        extracted = self._extract_fields(text)

        if "total" not in extracted:
            raise PDFExtractionError(
                message="No se pudo extraer el total / Could not extract total",
                file_path=pdf_path,
                partial_data=extracted,
            )

        return self._normalize_extracted(extracted, pdf_path)

    def _extract_text(self, pdf_path: str) -> str:
        """
        Extract all text from PDF using PyMuPDF.
        Extrae todo el texto del PDF usando PyMuPDF.

        Args / Argumentos:
            pdf_path: Path to PDF file / Ruta al archivo PDF

        Returns / Retorna:
            Concatenated text from all pages / Texto concatenado de todas las paginas
        """
        import fitz

        text_parts: list[str] = []
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text_parts.append(page.get_text())
        return "\n".join(text_parts)

    def _extract_fields(self, text: str) -> dict:
        """
        Extract all recognizable fields from text using regex patterns.
        Extrae todos los campos reconocibles del texto usando patrones regex.

        Args / Argumentos:
            text: Full text extracted from PDF / Texto completo del PDF

        Returns / Retorna:
            Dict with found field names and values / Dict con campos encontrados
        """
        extracted: dict[str, str] = {}

        for field_name, patterns in self.PATTERNS.items():
            value = self._find_pattern(text, patterns)
            if value is not None:
                extracted[field_name] = value.strip()

        logger.info(
            "PDF extraction found %d fields: %s",
            len(extracted),
            list(extracted.keys()),
        )
        return extracted

    def _find_pattern(
        self, text: str, patterns: list[str],
    ) -> Optional[str]:
        """
        Find first matching regex pattern in text.
        Busca el primer patron regex que coincida en el texto.

        Args / Argumentos:
            text: Text to search / Texto donde buscar
            patterns: List of regex patterns / Lista de patrones regex

        Returns / Retorna:
            Matched value or None / Valor encontrado o None
        """
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return (
                    match.group(1) if match.groups()
                    else match.group(0)
                )
        return None

    def _parse_amount(self, value: Optional[str]) -> float:
        """
        Parse currency amount string to float.
        Parsea cadena de monto monetario a float.

        Removes thousand separators: "1,234.56" -> 1234.56
        Elimina separadores de miles: "1,234.56" -> 1234.56

        Args / Argumentos:
            value: Amount string or None / Cadena de monto o None

        Returns / Retorna:
            Parsed float value or 0.0 / Valor float parseado o 0.0
        """
        if value is None:
            return 0.0
        try:
            cleaned = value.replace(",", "").replace("$", "").strip()
            return float(cleaned)
        except (ValueError, AttributeError):
            logger.warning("Could not parse amount: '%s'", value)
            return 0.0

    def _normalize_extracted(
        self, data: dict, source: str,
    ) -> dict:
        """
        Normalize extracted fields to mapper-compatible dict.
        Normaliza campos extraidos a dict compatible con mappers.

        Args / Argumentos:
            data: Raw extracted fields / Campos extraidos crudos
            source: Source file path / Ruta del archivo fuente

        Returns / Retorna:
            Normalized dict with standard field names
            Dict normalizado con nombres de campos estandar
        """
        normalized: dict = {
            "document_number": data.get("document_number"),
            "control_number": data.get("control_number"),
            "issue_date": data.get("date"),
            "supplier_name": data.get("supplier_name"),
            "supplier_nit": data.get("supplier_nit"),
            "supplier_nrc": data.get("supplier_nrc"),
            "subtotal": self._parse_amount(data.get("subtotal")),
            "tax": self._parse_amount(data.get("iva")),
            "total": self._parse_amount(data.get("total")),
            "source_file": source,
            "_extracted_from_pdf": True,
            "_extraction_fields_found": list(data.keys()),
        }
        return normalized
