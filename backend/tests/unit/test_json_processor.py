"""
JSONProcessor Tests / Pruebas del Procesador de JSON
====================================================

Unit tests for the JSONProcessor class.
Pruebas unitarias para la clase JSONProcessor.
"""

import json

import pytest

from src.core.json_processor import JSONProcessor, JSONProcessorError
from src.models.invoice import InvoiceType


class TestJSONProcessorInit:
    """Tests for JSONProcessor initialization."""

    def test_initialization(self):
        """Test that processor initializes correctly."""
        processor = JSONProcessor()
        assert processor.warnings == []

    def test_clear_warnings(self):
        """Test clearing warnings."""
        processor = JSONProcessor()
        processor.warnings = ["test warning"]
        processor.clear_warnings()
        assert processor.warnings == []


class TestProcessFile:
    """Tests for process_file method."""

    def test_process_valid_json_file(self, sample_json_file):
        """Test processing a valid JSON file."""
        processor = JSONProcessor()
        invoice = processor.process_file(str(sample_json_file))

        assert invoice.document_number == "FAC-001"
        assert invoice.invoice_type == InvoiceType.FACTURA
        assert invoice.customer_name == "Test Customer / Cliente de Prueba"
        assert len(invoice.items) == 2

    def test_process_file_sets_source_file(self, sample_json_file):
        """Test that source_file is set correctly."""
        processor = JSONProcessor()
        invoice = processor.process_file(str(sample_json_file))

        assert invoice.source_file == str(sample_json_file)

    def test_process_nonexistent_file_raises_error(self):
        """Test that nonexistent file raises error."""
        processor = JSONProcessor()

        with pytest.raises(JSONProcessorError) as exc_info:
            processor.process_file("/nonexistent/path/file.json")

        assert "not found" in exc_info.value.message.lower()

    def test_process_non_json_file_raises_error(self, tmp_path):
        """Test that non-JSON file raises error."""
        processor = JSONProcessor()

        txt_file = tmp_path / "test.txt"
        txt_file.write_text("not json")

        with pytest.raises(JSONProcessorError) as exc_info:
            processor.process_file(str(txt_file))

        assert "extension" in exc_info.value.message.lower()

    def test_process_invalid_json_raises_error(self, tmp_path):
        """Test that invalid JSON content raises error."""
        processor = JSONProcessor()

        json_file = tmp_path / "invalid.json"
        json_file.write_text("{invalid json content")

        with pytest.raises(JSONProcessorError) as exc_info:
            processor.process_file(str(json_file))

        assert "invalid json" in exc_info.value.message.lower()

    def test_process_json_missing_required_fields(self, tmp_path):
        """Test that JSON missing required fields raises error."""
        processor = JSONProcessor()

        json_file = tmp_path / "incomplete.json"
        json_file.write_text(json.dumps({"customer_name": "Test"}))

        with pytest.raises(JSONProcessorError) as exc_info:
            processor.process_file(str(json_file))

        assert "structure" in exc_info.value.message.lower()

    def test_process_minimal_valid_json(self, sample_json_data_minimal, tmp_path):
        """Test processing JSON with only required fields."""
        processor = JSONProcessor()

        json_file = tmp_path / "minimal.json"
        with open(json_file, "w") as f:
            json.dump(sample_json_data_minimal, f)

        invoice = processor.process_file(str(json_file))

        assert invoice.document_number == "FAC-002"
        assert invoice.items == []  # No items provided
        assert invoice.tax == 0  # Default tax


class TestProcessBatch:
    """Tests for process_batch method."""

    def test_process_batch_multiple_files(self, sample_json_files):
        """Test processing multiple JSON files."""
        processor = JSONProcessor()
        file_paths = [str(f) for f in sample_json_files]

        invoices = processor.process_batch(file_paths)

        assert len(invoices) == 3
        assert invoices[0].document_number == "FAC-001"
        assert invoices[1].document_number == "FAC-002"
        assert invoices[2].document_number == "FAC-003"

    def test_process_batch_empty_list(self):
        """Test processing empty file list."""
        processor = JSONProcessor()
        invoices = processor.process_batch([])

        assert invoices == []

    def test_process_batch_continues_on_error(self, sample_json_files, tmp_path):
        """Test that batch processing continues on error by default."""
        processor = JSONProcessor()

        # Add an invalid file to the batch
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{invalid}")

        file_paths = [str(sample_json_files[0]), str(invalid_file), str(sample_json_files[1])]

        invoices = processor.process_batch(file_paths)

        # Should have processed 2 valid files
        assert len(invoices) == 2

    def test_process_batch_stops_on_error_if_requested(self, sample_json_files, tmp_path):
        """Test that batch processing stops on error if requested."""
        processor = JSONProcessor()

        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{invalid}")

        file_paths = [str(invalid_file), str(sample_json_files[0])]

        with pytest.raises(JSONProcessorError):
            processor.process_batch(file_paths, stop_on_error=True)


class TestValidateJsonStructure:
    """Tests for validate_json_structure method."""

    def test_valid_structure(self, sample_json_data):
        """Test that valid structure passes."""
        processor = JSONProcessor()
        assert processor.validate_json_structure(sample_json_data) is True

    def test_missing_required_fields(self, sample_json_data_invalid):
        """Test that missing required fields fails."""
        processor = JSONProcessor()
        assert processor.validate_json_structure(sample_json_data_invalid) is False

    def test_non_dict_input(self):
        """Test that non-dict input fails."""
        processor = JSONProcessor()
        assert processor.validate_json_structure([1, 2, 3]) is False
        assert processor.validate_json_structure("string") is False

    def test_missing_optional_fields_generates_warnings(self, tmp_path):
        """Test that missing optional fields generate warnings."""
        processor = JSONProcessor()

        data = {
            "document_number": "FAC-001",
            "issue_date": "2025-02-04",
            "customer_name": "Test",
            "total": 100.00,
            # Missing: invoice_type, customer_id, items, subtotal, tax
        }

        processor.validate_json_structure(data)
        warnings = processor.get_warnings()

        assert len(warnings) > 0
        assert any("optional" in w.lower() for w in warnings)


class TestParseInvoiceType:
    """Tests for invoice type parsing."""

    def test_parse_factura_variations(self, sample_json_data, tmp_path):
        """Test parsing various factura type strings."""
        processor = JSONProcessor()

        for type_str in ["factura", "FACTURA", "invoice", "Invoice"]:
            data = sample_json_data.copy()
            data["invoice_type"] = type_str

            json_file = tmp_path / f"test_{type_str}.json"
            with open(json_file, "w") as f:
                json.dump(data, f)

            invoice = processor.process_file(str(json_file))
            assert invoice.invoice_type == InvoiceType.FACTURA

    def test_parse_ccf_variations(self, sample_json_data, tmp_path):
        """Test parsing CCF type strings."""
        processor = JSONProcessor()

        for type_str in ["ccf", "CCF", "credito_fiscal"]:
            data = sample_json_data.copy()
            data["invoice_type"] = type_str

            json_file = tmp_path / f"test_{type_str}.json"
            with open(json_file, "w") as f:
                json.dump(data, f)

            invoice = processor.process_file(str(json_file))
            assert invoice.invoice_type == InvoiceType.CCF

    def test_parse_nota_credito_variations(self, sample_json_data, tmp_path):
        """Test parsing nota_credito type strings."""
        processor = JSONProcessor()

        for type_str in ["nota_credito", "credit_note"]:
            data = sample_json_data.copy()
            data["invoice_type"] = type_str

            json_file = tmp_path / f"test_{type_str}.json"
            with open(json_file, "w") as f:
                json.dump(data, f)

            invoice = processor.process_file(str(json_file))
            assert invoice.invoice_type == InvoiceType.NOTA_CREDITO

    def test_parse_unknown_type_defaults_to_factura(self, sample_json_data, tmp_path):
        """Test that unknown type defaults to FACTURA with warning."""
        processor = JSONProcessor()

        data = sample_json_data.copy()
        data["invoice_type"] = "unknown_type"

        json_file = tmp_path / "test_unknown.json"
        with open(json_file, "w") as f:
            json.dump(data, f)

        invoice = processor.process_file(str(json_file))
        assert invoice.invoice_type == InvoiceType.FACTURA


class TestDecimalParsing:
    """Tests for decimal value parsing."""

    def test_parse_integer_values(self, sample_json_data, tmp_path):
        """Test parsing integer values."""
        processor = JSONProcessor()

        data = sample_json_data.copy()
        data["total"] = 100  # Integer
        data["subtotal"] = 90
        data["tax"] = 10

        json_file = tmp_path / "test_int.json"
        with open(json_file, "w") as f:
            json.dump(data, f)

        invoice = processor.process_file(str(json_file))
        assert invoice.total == 100

    def test_parse_string_values_with_comma(self, sample_json_data, tmp_path):
        """Test parsing string values with comma decimal separator."""
        processor = JSONProcessor()

        data = sample_json_data.copy()
        data["total"] = "100,50"  # European format

        json_file = tmp_path / "test_comma.json"
        with open(json_file, "w") as f:
            json.dump(data, f)

        invoice = processor.process_file(str(json_file))
        # Comma should be converted to decimal point
        assert str(invoice.total) == "100.50"


class TestWarnings:
    """Tests for warning handling."""

    def test_get_warnings_returns_copy(self):
        """Test that get_warnings returns a copy."""
        processor = JSONProcessor()
        processor.warnings = ["warning1", "warning2"]

        warnings = processor.get_warnings()
        warnings.append("warning3")

        assert len(processor.warnings) == 2

    def test_warnings_cleared_on_new_file(self, sample_json_files):
        """Test that warnings are cleared when processing new file."""
        processor = JSONProcessor()
        processor.warnings = ["old warning"]

        processor.process_file(str(sample_json_files[0]))

        # Old warning should be cleared
        assert "old warning" not in processor.warnings
