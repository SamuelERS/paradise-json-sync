"""
Format Detector / Detector de Formato
======================================

Intelligent format detection for purchase invoice JSON files.
Deteccion inteligente de formato para archivos JSON de facturas de compra.

This module provides / Este modulo provee:
- DetectedFormat: Enum of recognized invoice formats (6 values)
- DetectionResult: Pydantic model with detection results
- FormatDetector: Main detector class with fingerprinting algorithm
"""

import logging
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# === Confidence thresholds / Umbrales de confianza ===
CONFIDENCE_HIGH = 0.90
CONFIDENCE_MEDIUM = 0.70
CONFIDENCE_LOW = 0.50


class DetectedFormat(str, Enum):
    """
    Recognized invoice formats / Formatos de factura reconocidos.

    Each value represents a distinct JSON structure for purchase invoices.
    Cada valor representa una estructura JSON distinta para facturas de compra.
    """

    DTE_STANDARD = "DTE_STANDARD"
    DTE_VARIANT_A = "DTE_VARIANT_A"
    DTE_VARIANT_B = "DTE_VARIANT_B"
    GENERIC_FLAT = "GENERIC_FLAT"
    PDF_EXTRACTED = "PDF_EXTRACTED"
    UNKNOWN = "UNKNOWN"


class DetectionResult(BaseModel):
    """
    Format detection result / Resultado de deteccion de formato.

    Contains the detected format, confidence score, and debug info.
    Contiene el formato detectado, puntaje de confianza e info de debug.
    """

    format: DetectedFormat = Field(
        description="Detected format / Formato identificado",
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score 0.0-1.0 / Puntaje de confianza",
    )
    confidence_level: str = Field(
        description="HIGH (>=0.90), MEDIUM (>=0.70), LOW (>=0.50), NONE (<0.50)",
    )
    scores: dict[str, float] = Field(
        default_factory=dict,
        description="Scores for all formats (debug) / Puntajes de todos los formatos",
    )
    items_key: Optional[str] = Field(
        default=None,
        description="Key where items are located / Clave donde estan los items",
    )
    total_key: Optional[str] = Field(
        default=None,
        description="Key where total is located / Clave donde esta el total",
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Additional detection info / Info adicional de deteccion",
    )


# === Fingerprint definitions / Definiciones de fingerprints ===

FINGERPRINT_DTE_STANDARD: dict = {
    "required_keys": {
        "identificacion", "emisor", "receptor",
        "cuerpoDocumento", "resumen",
    },
    "optional_keys": {"apendice", "extension", "otrosDocumentos"},
    "nested_checks": {
        "identificacion": {"codigoGeneracion", "tipoDte", "fecEmi"},
        "resumen": {"totalPagar"},
    },
    "items_key": "cuerpoDocumento",
}

FINGERPRINT_DTE_VARIANT_A: dict = {
    "required_keys": {"identificacion", "emisor", "receptor", "detalle"},
    "nested_checks": {
        "identificacion": {"codigoGeneracion"},
    },
    "items_key": "detalle",
    "total_key_alternatives": ["totalAPagar", "montoTotalOperacion"],
}

FINGERPRINT_DTE_VARIANT_B: dict = {
    "required_keys": {"identificacion", "emisor", "cuerpoDocumento"},
    "root_total_keys": {"totalPagar", "totalGravada", "totalIva"},
    "items_key": "cuerpoDocumento",
}

FINGERPRINT_GENERIC_FLAT: dict = {
    "heuristic_keys": {
        "invoice_number": [
            "numero_factura", "numero", "factura_no",
            "invoice_number", "no_factura",
        ],
        "date": ["fecha", "fecha_emision", "date", "fecEmi"],
        "supplier": ["proveedor", "emisor", "vendor", "supplier"],
        "total": ["total", "totalPagar", "monto_total", "total_amount"],
    },
}


def _get_confidence_level(score: float) -> str:
    """
    Map a numeric score to a confidence level string.
    Mapea un puntaje numerico a un nivel de confianza.

    Args / Argumentos:
        score: Numeric score between 0.0 and 1.0

    Returns / Retorna:
        One of "HIGH", "MEDIUM", "LOW", "NONE"
    """
    if score >= CONFIDENCE_HIGH:
        return "HIGH"
    if score >= CONFIDENCE_MEDIUM:
        return "MEDIUM"
    if score >= CONFIDENCE_LOW:
        return "LOW"
    return "NONE"


class FormatDetector:
    """
    Intelligent format detector for purchase invoice JSONs.
    Detector inteligente de formato para JSONs de facturas de compra.

    Uses fingerprinting to compare JSON structure against known formats.
    Usa fingerprinting para comparar estructura JSON contra formatos conocidos.
    """

    def __init__(self) -> None:
        """
        Initialize detector with default fingerprints.
        Inicializa el detector con fingerprints predeterminados.
        """
        self.fingerprints: dict[DetectedFormat, dict] = {}
        self._register_default_formats()

    def _register_default_formats(self) -> None:
        """
        Register the 4 built-in fingerprints.
        Registra los 4 fingerprints predeterminados.
        """
        self.fingerprints[DetectedFormat.DTE_STANDARD] = (
            FINGERPRINT_DTE_STANDARD
        )
        self.fingerprints[DetectedFormat.DTE_VARIANT_A] = (
            FINGERPRINT_DTE_VARIANT_A
        )
        self.fingerprints[DetectedFormat.DTE_VARIANT_B] = (
            FINGERPRINT_DTE_VARIANT_B
        )
        self.fingerprints[DetectedFormat.GENERIC_FLAT] = (
            FINGERPRINT_GENERIC_FLAT
        )

    def register_format(
        self,
        format_type: DetectedFormat,
        fingerprint: dict,
    ) -> None:
        """
        Register a new format fingerprint dynamically.
        Registra un nuevo fingerprint de formato dinamicamente.

        Args / Argumentos:
            format_type: The DetectedFormat enum value
            fingerprint: Dictionary describing the format structure
        """
        self.fingerprints[format_type] = fingerprint
        logger.info("Registered format: %s", format_type.value)

    def detect(self, data: dict) -> DetectionResult:
        """
        Analyze a JSON dict and determine its format.
        Analiza un dict JSON y determina su formato.

        Args / Argumentos:
            data: Parsed JSON dictionary to analyze

        Returns / Retorna:
            DetectionResult with format, confidence, and details
        """
        if not data or not isinstance(data, dict):
            return self._empty_result()

        scores, items_keys, total_keys = self._score_all(data)
        best_fmt = max(scores, key=scores.get)  # type: ignore[arg-type]
        best_score = scores[best_fmt]
        level = _get_confidence_level(best_score)

        if level == "NONE":
            return DetectionResult(
                format=DetectedFormat.UNKNOWN,
                confidence=best_score,
                confidence_level="NONE",
                scores=scores,
            )

        logger.info(
            "Detected format: %s (confidence: %.2f, level: %s)",
            best_fmt, best_score, level,
        )
        return DetectionResult(
            format=DetectedFormat(best_fmt),
            confidence=best_score,
            confidence_level=level,
            scores=scores,
            items_key=items_keys.get(best_fmt),
            total_key=total_keys.get(best_fmt),
        )

    def _empty_result(self) -> DetectionResult:
        """
        Build an UNKNOWN result for empty/invalid input.
        Construye un resultado UNKNOWN para entrada vacia/invalida.
        """
        return DetectionResult(
            format=DetectedFormat.UNKNOWN,
            confidence=0.0,
            confidence_level="NONE",
            scores={f.value: 0.0 for f in self.fingerprints},
        )

    def _score_all(
        self, data: dict,
    ) -> tuple[dict[str, float], dict[str, Optional[str]], dict[str, Optional[str]]]:
        """
        Score data against all registered fingerprints.
        Puntua datos contra todos los fingerprints registrados.
        """
        scores: dict[str, float] = {}
        items_keys: dict[str, Optional[str]] = {}
        total_keys: dict[str, Optional[str]] = {}
        for fmt, fp in self.fingerprints.items():
            scores[fmt.value] = round(self._calculate_score(data, fp), 4)
            items_keys[fmt.value] = fp.get("items_key")
            total_keys[fmt.value] = self._find_total_key(data, fp)
        return scores, items_keys, total_keys

    def _calculate_score(
        self,
        data: dict,
        fingerprint: dict,
    ) -> float:
        """
        Calculate how well a JSON matches a fingerprint.
        Calcula que tan bien un JSON coincide con un fingerprint.

        Scoring weights / Pesos del puntaje:
        - Required keys present: 40% (proportional)
        - Nested keys present: 30% (proportional)
        - Optional keys present: 10% (bonus)
        - Value types correct: 20%

        Args / Argumentos:
            data: The JSON dict to score
            fingerprint: The fingerprint to compare against

        Returns / Retorna:
            Score from 0.0 to 1.0
        """
        if "heuristic_keys" in fingerprint:
            return self._calculate_heuristic_score(data, fingerprint)

        score = 0.0
        score += self._score_required_keys(data, fingerprint) * 0.4
        score += self._score_nested_keys(data, fingerprint) * 0.3
        score += self._score_optional_keys(data, fingerprint) * 0.1
        score += self._check_value_types(data, fingerprint) * 0.2
        return min(score, 1.0)

    def _score_required_keys(
        self,
        data: dict,
        fingerprint: dict,
    ) -> float:
        """
        Score presence of required keys (0.0 to 1.0).
        Puntua la presencia de claves requeridas (0.0 a 1.0).
        """
        required = fingerprint.get("required_keys", set())
        if not required:
            return 1.0
        present = required.intersection(data.keys())
        return len(present) / len(required)

    def _score_nested_keys(
        self,
        data: dict,
        fingerprint: dict,
    ) -> float:
        """
        Score presence of nested (child) keys (0.0 to 1.0).
        Puntua la presencia de claves anidadas (hijas) (0.0 a 1.0).
        """
        nested = fingerprint.get("nested_checks", {})
        if not nested:
            return 1.0
        nested_score = 0.0
        for parent_key, child_keys in nested.items():
            if parent_key in data and isinstance(data[parent_key], dict):
                present = child_keys.intersection(
                    data[parent_key].keys(),
                )
                nested_score += len(present) / len(child_keys)
        return nested_score / len(nested)

    def _score_optional_keys(
        self,
        data: dict,
        fingerprint: dict,
    ) -> float:
        """
        Score presence of optional keys (0.0 to 1.0).
        Puntua la presencia de claves opcionales (0.0 a 1.0).
        """
        optional = fingerprint.get("optional_keys", set())
        if not optional:
            return 0.0
        present = optional.intersection(data.keys())
        return len(present) / len(optional)

    def _check_value_types(
        self,
        data: dict,
        fingerprint: dict,
    ) -> float:
        """
        Check that values have expected types for DTE detection.
        Verifica que los valores tengan los tipos esperados para DTE.

        Args / Argumentos:
            data: The JSON dict to check
            fingerprint: The fingerprint with type expectations

        Returns / Retorna:
            Score from 0.0 to 1.0
        """
        passed, total = 0, 0

        p, t = self._check_ident_types(data)
        passed += p
        total += t

        p, t = self._check_items_type(data, fingerprint)
        passed += p
        total += t

        p, t = self._check_summary_type(data, fingerprint)
        passed += p
        total += t

        if total == 0:
            return 0.0
        return passed / total

    def _check_ident_types(self, data: dict) -> tuple[int, int]:
        """
        Check identificacion.version (int) and tipoDte (str).
        Verifica identificacion.version (int) y tipoDte (str).
        """
        passed, total = 0, 0
        ident = data.get("identificacion")
        if isinstance(ident, dict):
            total += 1
            if isinstance(ident.get("version"), int):
                passed += 1
            total += 1
            if isinstance(ident.get("tipoDte"), str):
                passed += 1
        return passed, total

    def _check_items_type(
        self, data: dict, fingerprint: dict,
    ) -> tuple[int, int]:
        """
        Check that the items key value is a list.
        Verifica que el valor de la clave de items sea una lista.
        """
        items_key = fingerprint.get("items_key")
        if not items_key:
            return 0, 0
        is_list = isinstance(data.get(items_key), list)
        return (1 if is_list else 0), 1

    def _check_summary_type(
        self, data: dict, fingerprint: dict,
    ) -> tuple[int, int]:
        """
        Check resumen/totales is dict and root_total_keys exist.
        Verifica que resumen/totales sea dict y root_total_keys existan.
        """
        passed, total = 0, 0
        for key in ("resumen", "totales"):
            if key in data:
                total += 1
                if isinstance(data[key], dict):
                    passed += 1
        root_keys = fingerprint.get("root_total_keys", set())
        if root_keys:
            total += 1
            if root_keys.intersection(data.keys()):
                passed += 1
        return passed, total

    def _calculate_heuristic_score(
        self,
        data: dict,
        fingerprint: dict,
    ) -> float:
        """
        Calculate score for GENERIC_FLAT using heuristic key matching.
        Calcula puntaje para GENERIC_FLAT usando coincidencia heuristica.

        For each category (invoice_number, date, supplier, total),
        checks if any synonym is present in the JSON keys.
        Para cada categoria, verifica si algun sinonimo esta presente.

        Args / Argumentos:
            data: The JSON dict to score
            fingerprint: Fingerprint with heuristic_keys

        Returns / Retorna:
            Score from 0.0 to 1.0
        """
        heuristic = fingerprint.get("heuristic_keys", {})
        if not heuristic:
            return 0.0

        categories_found = 0
        data_keys = set(data.keys())

        for _category, synonyms in heuristic.items():
            synonym_set = set(synonyms)
            if synonym_set.intersection(data_keys):
                categories_found += 1

        return categories_found / len(heuristic)

    def _find_total_key(
        self,
        data: dict,
        fingerprint: dict,
    ) -> Optional[str]:
        """
        Find the actual total key in the data based on fingerprint.
        Encuentra la clave de total real en los datos segun el fingerprint.

        Args / Argumentos:
            data: The JSON dict to search
            fingerprint: The fingerprint with total key info

        Returns / Retorna:
            The found total key name, or None
        """
        # Check total_key_alternatives
        for key in fingerprint.get("total_key_alternatives", []):
            if key in data:
                return key

        # Check root_total_keys
        for key in fingerprint.get("root_total_keys", set()):
            if key in data:
                return key

        # Check nested resumen.totalPagar
        nested = fingerprint.get("nested_checks", {})
        if "resumen" in nested and "resumen" in data:
            resumen = data["resumen"]
            if isinstance(resumen, dict) and "totalPagar" in resumen:
                return "resumen.totalPagar"

        return None
