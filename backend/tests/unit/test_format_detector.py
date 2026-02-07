"""
Format Detector Tests / Pruebas del Detector de Formato
========================================================

Unit tests for FormatDetector, DetectedFormat, and DetectionResult.
Pruebas unitarias para FormatDetector, DetectedFormat y DetectionResult.

Coverage target / Objetivo de cobertura: >= 70%
"""

import pytest

from src.core.purchases.format_detector import (
    CONFIDENCE_HIGH,
    CONFIDENCE_LOW,
    CONFIDENCE_MEDIUM,
    DetectedFormat,
    DetectionResult,
    FormatDetector,
    _get_confidence_level,
)


class TestDetectedFormat:
    """Tests for DetectedFormat enum / Pruebas para enum DetectedFormat."""

    def test_all_formats_exist(self):
        """Test that all 6 format values exist in the enum.
        Verifica que los 6 valores de formato existan en el enum."""
        expected = {
            "DTE_STANDARD",
            "DTE_VARIANT_A",
            "DTE_VARIANT_B",
            "GENERIC_FLAT",
            "PDF_EXTRACTED",
            "UNKNOWN",
        }
        actual = {member.value for member in DetectedFormat}
        assert actual == expected

    def test_format_is_string_enum(self):
        """Test that DetectedFormat inherits from str.
        Verifica que DetectedFormat hereda de str."""
        assert isinstance(DetectedFormat.DTE_STANDARD, str)
        assert DetectedFormat.DTE_STANDARD == "DTE_STANDARD"


class TestDetectionResult:
    """Tests for DetectionResult model / Pruebas para modelo DetectionResult."""

    def test_create_result(self):
        """Test creating a DetectionResult with all fields.
        Verifica la creacion de DetectionResult con todos los campos."""
        result = DetectionResult(
            format=DetectedFormat.DTE_STANDARD,
            confidence=0.95,
            confidence_level="HIGH",
            scores={"DTE_STANDARD": 0.95, "UNKNOWN": 0.0},
            items_key="cuerpoDocumento",
            total_key="resumen.totalPagar",
            metadata={"note": "test"},
        )
        assert result.format == DetectedFormat.DTE_STANDARD
        assert result.confidence == 0.95
        assert result.confidence_level == "HIGH"
        assert "DTE_STANDARD" in result.scores
        assert result.items_key == "cuerpoDocumento"
        assert result.total_key == "resumen.totalPagar"
        assert result.metadata == {"note": "test"}

    def test_create_result_defaults(self):
        """Test DetectionResult with default optional fields.
        Verifica DetectionResult con campos opcionales por defecto."""
        result = DetectionResult(
            format=DetectedFormat.UNKNOWN,
            confidence=0.0,
            confidence_level="NONE",
        )
        assert result.scores == {}
        assert result.items_key is None
        assert result.total_key is None
        assert result.metadata == {}


class TestConfidenceLevels:
    """Tests for confidence level mapping / Pruebas para mapeo de confianza."""

    def test_confidence_levels(self):
        """Test HIGH/MEDIUM/LOW/NONE thresholds.
        Verifica umbrales HIGH/MEDIUM/LOW/NONE."""
        assert _get_confidence_level(0.95) == "HIGH"
        assert _get_confidence_level(0.90) == "HIGH"
        assert _get_confidence_level(0.85) == "MEDIUM"
        assert _get_confidence_level(0.70) == "MEDIUM"
        assert _get_confidence_level(0.60) == "LOW"
        assert _get_confidence_level(0.50) == "LOW"
        assert _get_confidence_level(0.49) == "NONE"
        assert _get_confidence_level(0.0) == "NONE"

    def test_confidence_constants(self):
        """Test that confidence constants have correct values.
        Verifica que las constantes de confianza sean correctas."""
        assert CONFIDENCE_HIGH == 0.90
        assert CONFIDENCE_MEDIUM == 0.70
        assert CONFIDENCE_LOW == 0.50


class TestFormatDetector:
    """Tests for FormatDetector class / Pruebas para clase FormatDetector."""

    def test_detect_dte_standard(self, sample_dte_standard_json):
        """Test detection of DTE_STANDARD format (Hacienda official).
        Verifica deteccion del formato DTE_STANDARD (oficial Hacienda)."""
        detector = FormatDetector()
        result = detector.detect(sample_dte_standard_json)

        assert result.format == DetectedFormat.DTE_STANDARD
        assert result.confidence_level == "HIGH"
        assert result.confidence >= CONFIDENCE_HIGH
        assert result.items_key == "cuerpoDocumento"

    def test_detect_dte_variant_a(self, sample_dte_variant_a_json):
        """Test detection of DTE_VARIANT_A (items in 'detalle').
        Verifica deteccion de DTE_VARIANT_A (items en 'detalle')."""
        detector = FormatDetector()
        result = detector.detect(sample_dte_variant_a_json)

        assert result.format == DetectedFormat.DTE_VARIANT_A
        assert result.confidence >= CONFIDENCE_LOW
        assert result.items_key == "detalle"

    def test_detect_dte_variant_b(self, sample_dte_variant_b_json):
        """Test detection of DTE_VARIANT_B (flattened summary).
        Verifica deteccion de DTE_VARIANT_B (resumen aplanado)."""
        detector = FormatDetector()
        result = detector.detect(sample_dte_variant_b_json)

        assert result.format == DetectedFormat.DTE_VARIANT_B
        assert result.confidence >= CONFIDENCE_LOW
        assert result.items_key == "cuerpoDocumento"

    def test_detect_generic_flat(self, sample_generic_flat_json):
        """Test detection of GENERIC_FLAT format (common field names).
        Verifica deteccion de formato GENERIC_FLAT (nombres comunes)."""
        detector = FormatDetector()
        result = detector.detect(sample_generic_flat_json)

        assert result.format == DetectedFormat.GENERIC_FLAT
        assert result.confidence >= CONFIDENCE_LOW

    def test_detect_unknown(self, sample_unknown_json):
        """Test detection of UNKNOWN format (no matching fingerprint).
        Verifica deteccion de formato UNKNOWN (sin fingerprint)."""
        detector = FormatDetector()
        result = detector.detect(sample_unknown_json)

        assert result.format == DetectedFormat.UNKNOWN
        assert result.confidence_level == "NONE"
        assert result.confidence < CONFIDENCE_LOW

    def test_scores_all_formats(self, sample_dte_standard_json):
        """Test that scores dict contains all registered formats.
        Verifica que scores contiene todos los formatos registrados."""
        detector = FormatDetector()
        result = detector.detect(sample_dte_standard_json)

        assert "DTE_STANDARD" in result.scores
        assert "DTE_VARIANT_A" in result.scores
        assert "DTE_VARIANT_B" in result.scores
        assert "GENERIC_FLAT" in result.scores
        assert len(result.scores) == 4

    def test_empty_json(self):
        """Test detection with empty JSON dict.
        Verifica deteccion con dict JSON vacio."""
        detector = FormatDetector()
        result = detector.detect({})

        assert result.format == DetectedFormat.UNKNOWN
        assert result.confidence_level == "NONE"
        assert result.confidence == 0.0

    def test_register_new_format(self):
        """Test dynamically registering a new format and detecting it.
        Verifica registro dinamico de nuevo formato y su deteccion."""
        detector = FormatDetector()

        new_fingerprint = {
            "required_keys": {"factura", "proveedor", "lineas"},
            "nested_checks": {"factura": {"numero", "fecha"}},
            "items_key": "lineas",
        }
        detector.register_format(
            DetectedFormat.PDF_EXTRACTED,
            new_fingerprint,
        )

        test_data = {
            "factura": {"numero": "F-001", "fecha": "2026-01-01"},
            "proveedor": {"nombre": "Test"},
            "lineas": [{"item": 1}],
        }
        result = detector.detect(test_data)

        assert result.format == DetectedFormat.PDF_EXTRACTED
        assert result.confidence >= CONFIDENCE_LOW

    def test_items_key_detected(self, sample_dte_standard_json):
        """Test that items_key is correctly identified per format.
        Verifica que items_key se identifica correctamente por formato."""
        detector = FormatDetector()
        result = detector.detect(sample_dte_standard_json)

        assert result.items_key == "cuerpoDocumento"

    def test_total_key_detected_standard(self, sample_dte_standard_json):
        """Test that total_key is found in DTE_STANDARD resumen.
        Verifica que total_key se encuentra en resumen de DTE_STANDARD."""
        detector = FormatDetector()
        result = detector.detect(sample_dte_standard_json)

        assert result.total_key == "resumen.totalPagar"

    def test_none_input(self):
        """Test detection with None-like input (not a dict).
        Verifica deteccion con entrada tipo None (no es dict)."""
        detector = FormatDetector()
        result = detector.detect(None)  # type: ignore[arg-type]

        assert result.format == DetectedFormat.UNKNOWN
        assert result.confidence == 0.0

    def test_default_formats_registered(self):
        """Test that 4 default formats are registered on init.
        Verifica que 4 formatos predeterminados se registran al iniciar."""
        detector = FormatDetector()

        assert len(detector.fingerprints) == 4
        assert DetectedFormat.DTE_STANDARD in detector.fingerprints
        assert DetectedFormat.DTE_VARIANT_A in detector.fingerprints
        assert DetectedFormat.DTE_VARIANT_B in detector.fingerprints
        assert DetectedFormat.GENERIC_FLAT in detector.fingerprints
