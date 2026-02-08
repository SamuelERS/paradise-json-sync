"""
Tests for PDF Extractor and PDF Extracted Mapper.
Tests para el Extractor de PDF y el Mapper de PDF Extraido.

Covers:
- PDFExtractor text extraction and field parsing
- Pattern matching for control numbers, NITs, dates, totals
- PDFExtractedMapper mapping to PurchaseInvoice
- Error handling for PDFs without text or totals
"""

import pytest

from src.core.purchases.pdf_extractor import PDFExtractionError, PDFExtractor
from src.core.purchases.mappers.pdf_extracted import PDFExtractedMapper
from src.models.purchase_invoice import PurchaseDocumentType

# === Sample PDF text content for tests ===

SAMPLE_PDF_TEXT_FULL = """
DOCUMENTO TRIBUTARIO ELECTRONICO
Número de Control: DTE-03-00000001-000000000000001
Código de Generación: A1B2C3D4-E5F6-7890-ABCD-EF1234567890
Fecha de Emisión: 06/02/2026
Emisor: DISTRIBUIDORA ABC S.A. DE C.V.
NIT: 0614-123456-789-0
NRC: 12345-6
SubTotal: $35.00
IVA: $4.55
Total a Pagar: $39.55
"""

SAMPLE_PDF_TEXT_PARTIAL = """
FACTURA DE COMPRA
Emisor: SERVICIOS XYZ
TOTAL: $100.00
"""

SAMPLE_PDF_TEXT_NO_TOTAL = """
DOCUMENTO TRIBUTARIO ELECTRONICO DE EL SALVADOR
Emisor: EMPRESA ABC S.A. DE C.V.
Fecha: 2026-02-08
Direccion: San Salvador, El Salvador, Centro America
"""


def _create_test_pdf(tmp_path, text_content: str) -> str:
    """
    Create a test PDF with the given text content.
    Crea un PDF de prueba con el texto dado.
    """
    import fitz

    path = str(tmp_path / "test_invoice.pdf")
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text_content, fontsize=10)
    doc.save(path)
    doc.close()
    return path


def _create_empty_pdf(tmp_path) -> str:
    """
    Create a PDF with no text (empty page).
    Crea un PDF sin texto (pagina vacia).
    """
    import fitz

    path = str(tmp_path / "empty.pdf")
    doc = fitz.open()
    doc.new_page()
    doc.save(path)
    doc.close()
    return path


# ============================================================
# TestPDFExtraction
# ============================================================


class TestPDFExtraction:
    """Tests for PDFExtractor.extract() method."""

    def test_extract_digital_pdf(self, tmp_path):
        """PDF with text extracts fields correctly."""
        pdf_path = _create_test_pdf(tmp_path, SAMPLE_PDF_TEXT_FULL)
        extractor = PDFExtractor()
        result = extractor.extract(pdf_path)

        assert result["_extracted_from_pdf"] is True
        assert result["source_file"] == pdf_path
        assert result["total"] > 0

    def test_extract_all_fields(self, tmp_path):
        """PDF with all fields finds all of them."""
        pdf_path = _create_test_pdf(tmp_path, SAMPLE_PDF_TEXT_FULL)
        extractor = PDFExtractor()
        result = extractor.extract(pdf_path)

        assert result["control_number"] is not None
        assert "DTE-03" in result["control_number"]
        assert result["document_number"] is not None
        assert result["issue_date"] is not None
        assert result["supplier_name"] is not None
        assert result["supplier_nit"] is not None
        assert result["supplier_nrc"] is not None
        assert result["subtotal"] == 35.00
        assert result["tax"] == 4.55
        assert result["total"] == 39.55

    def test_extract_partial_fields(self, tmp_path):
        """PDF with some fields finds those available."""
        pdf_path = _create_test_pdf(tmp_path, SAMPLE_PDF_TEXT_PARTIAL)
        extractor = PDFExtractor()
        result = extractor.extract(pdf_path)

        assert result["total"] == 100.00
        assert result["supplier_name"] is not None
        assert "SERVICIOS XYZ" in result["supplier_name"]
        assert result["control_number"] is None
        assert result["document_number"] is None

    def test_extract_no_text(self, tmp_path):
        """PDF without text raises PDFExtractionError."""
        pdf_path = _create_empty_pdf(tmp_path)
        extractor = PDFExtractor()

        with pytest.raises(PDFExtractionError, match="sin texto"):
            extractor.extract(pdf_path)

    def test_extract_no_total(self, tmp_path):
        """PDF with text but no total raises PDFExtractionError."""
        pdf_path = _create_test_pdf(tmp_path, SAMPLE_PDF_TEXT_NO_TOTAL)
        extractor = PDFExtractor()

        with pytest.raises(PDFExtractionError, match="total") as exc_info:
            extractor.extract(pdf_path)

        assert exc_info.value.partial_data is not None
        assert len(exc_info.value.partial_data) > 0


# ============================================================
# TestPatternMatching
# ============================================================


class TestPatternMatching:
    """Tests for PDFExtractor regex pattern matching."""

    def setup_method(self):
        """Create extractor instance for each test."""
        self.extractor = PDFExtractor()

    def test_pattern_control_number(self):
        """Regex matches DTE control number format."""
        text = "Número de Control: DTE-03-00000001-000000000000001"
        result = self.extractor._find_pattern(
            text, PDFExtractor.PATTERNS["control_number"],
        )
        assert result is not None
        assert "DTE-03" in result

    def test_pattern_nit(self):
        """Regex matches NIT format XXXX-XXXXXX-XXX-X."""
        text = "NIT: 0614-123456-789-0"
        result = self.extractor._find_pattern(
            text, PDFExtractor.PATTERNS["supplier_nit"],
        )
        assert result is not None
        assert "0614-123456-789-0" in result

    def test_pattern_total_formats(self):
        """Regex matches various total formats."""
        test_cases = [
            ("Total a Pagar: $1,234.56", 1234.56),
            ("TOTAL: $100.00", 100.00),
            ("Total Pagar: $50.00", 50.00),
        ]
        for text, expected in test_cases:
            result = self.extractor._find_pattern(
                text, PDFExtractor.PATTERNS["total"],
            )
            assert result is not None, f"Failed for: {text}"
            assert self.extractor._parse_amount(result) == expected

    def test_pattern_date_formats(self):
        """Regex matches various date formats."""
        test_cases = [
            "Fecha de Emisión: 06/02/2026",
            "Fecha: 2026-02-08",
            "Fecha: 08-02-2026",
        ]
        for text in test_cases:
            result = self.extractor._find_pattern(
                text, PDFExtractor.PATTERNS["date"],
            )
            assert result is not None, f"Failed for: {text}"

    def test_parse_amount(self):
        """_parse_amount handles various inputs correctly."""
        assert self.extractor._parse_amount("1,234.56") == 1234.56
        assert self.extractor._parse_amount("100.00") == 100.00
        assert self.extractor._parse_amount("$50.00") == 50.00
        assert self.extractor._parse_amount(None) == 0.0
        assert self.extractor._parse_amount("invalid") == 0.0


# ============================================================
# TestPDFExtractedMapper
# ============================================================


class TestPDFExtractedMapper:
    """Tests for PDFExtractedMapper."""

    def setup_method(self):
        """Create mapper instance for each test."""
        self.mapper = PDFExtractedMapper()

    def test_can_handle_pdf_data(self):
        """Data with _extracted_from_pdf=True is handled."""
        data = {"_extracted_from_pdf": True, "total": 100.0}
        assert self.mapper.can_handle(data) is True

    def test_can_handle_non_pdf(self):
        """Normal data without flag is not handled."""
        data = {"total": 100.0}
        assert self.mapper.can_handle(data) is False

        data_false = {"_extracted_from_pdf": False, "total": 100.0}
        assert self.mapper.can_handle(data_false) is False

    def test_map_creates_purchase_invoice(self):
        """Mapping generates a valid PurchaseInvoice."""
        data = {
            "_extracted_from_pdf": True,
            "_extraction_fields_found": ["total", "supplier_name"],
            "document_number": "A1B2C3D4-E5F6-7890-ABCD-EF1234567890",
            "control_number": "DTE-03-00000001-000000000000001",
            "issue_date": "06/02/2026",
            "supplier_name": "DISTRIBUIDORA ABC",
            "supplier_nit": "0614-123456-789-0",
            "subtotal": 35.00,
            "tax": 4.55,
            "total": 39.55,
        }
        invoice = self.mapper.map(data, source_file="/tmp/test.pdf")

        assert invoice.document_number == "A1B2C3D4-E5F6-7890-ABCD-EF1234567890"
        assert invoice.control_number == "DTE-03-00000001-000000000000001"
        assert invoice.supplier.name == "DISTRIBUIDORA ABC"
        assert invoice.detected_format == "PDF_EXTRACTED"
        assert invoice.detection_confidence == 0.5

    def test_map_adds_processing_warnings(self):
        """Mapped invoice has 'verificar manualmente' warning."""
        data = {
            "_extracted_from_pdf": True,
            "_extraction_fields_found": ["total"],
            "total": 100.0,
        }
        invoice = self.mapper.map(data, source_file="/tmp/test.pdf")

        warning_texts = " ".join(invoice.processing_warnings)
        assert "verificar manualmente" in warning_texts
        assert "Campos encontrados" in warning_texts

    def test_map_defaults_for_missing(self):
        """Missing fields get sensible defaults."""
        data = {
            "_extracted_from_pdf": True,
            "_extraction_fields_found": ["total"],
            "total": 50.0,
        }
        invoice = self.mapper.map(data, source_file="/tmp/factura.pdf")

        assert invoice.document_number == "PDF-factura"
        assert invoice.supplier.name == "Proveedor Desconocido"
        assert invoice.document_type == PurchaseDocumentType.DESCONOCIDO
        assert invoice.issue_date is not None

    def test_map_raw_data_is_none(self):
        """raw_data is always None for PDF-extracted invoices."""
        data = {
            "_extracted_from_pdf": True,
            "_extraction_fields_found": ["total"],
            "total": 100.0,
        }
        invoice = self.mapper.map(data, source_file="/tmp/test.pdf")

        assert invoice.raw_data is None
