"""
Purchase Processor Service / Servicio Procesador de Compras
============================================================

Orchestrator service that connects the full purchase processing pipeline.
Servicio orquestador que conecta el pipeline completo de procesamiento.

This module provides / Este modulo provee:
- PurchaseProcessorService: Pipeline orchestrator (detect -> map -> validate)
  Orquestador del pipeline (detectar -> mapear -> validar)

NOTE: Export functionality (PurchaseExporter) will be added in FASE 6.
NOTA: La funcionalidad de exportacion se agregara en FASE 6.
"""

import asyncio
import json
import logging
from json import JSONDecodeError
from pathlib import Path
from typing import Callable, Optional

from src.api.schemas.purchases import ProcessingResult
from src.core.purchases.base_mapper import MappingError
from src.core.purchases.format_detector import FormatDetector
from src.core.purchases.mapper_registry import create_default_registry
from src.core.purchases.validator import (
    PurchaseValidator,
    ValidationLevel,
)
from src.models.purchase_invoice import PurchaseInvoice

logger = logging.getLogger(__name__)

ProgressCallback = Optional[
    Callable[[int, int, str], None]
]


class PurchaseProcessorService:
    """
    Orchestrates purchase invoice processing pipeline.
    Orquesta el pipeline de procesamiento de facturas de compra.

    Pipeline: detect -> map -> validate -> (export in FASE 6)
    """

    def __init__(self) -> None:
        """
        Initialize service with all pipeline components.
        Inicializa servicio con todos los componentes del pipeline.
        """
        self.detector = FormatDetector()
        self.registry = create_default_registry()
        self.validator = PurchaseValidator()

    async def process(
        self,
        file_paths: list[str],
        config: object,
        progress_callback: ProgressCallback = None,
    ) -> ProcessingResult:
        """Execute full pipeline on files. / Ejecuta pipeline completo."""
        invoices: list[PurchaseInvoice] = []
        errors: list[dict] = []

        for i, path in enumerate(file_paths):
            if progress_callback:
                cb_result = progress_callback(
                    i + 1, len(file_paths), f"Procesando {Path(path).name}"
                )
                if asyncio.iscoroutine(cb_result):
                    await cb_result
            result = self._process_single(path, invoices)
            if isinstance(result, PurchaseInvoice):
                invoices.append(result)
            else:
                errors.append(result)

        return ProcessingResult(
            invoices=[inv.model_dump(mode="json") for inv in invoices],
            invoice_count=len(invoices),
            error_count=len(errors),
            errors=errors,
            formats_summary=self._count_formats(invoices),
        )

    def _process_single(
        self, path: str, existing: list[PurchaseInvoice]
    ) -> PurchaseInvoice | dict:
        """Process a single file. Returns invoice or error dict."""
        try:
            raw_data = self._load_json(path)
            detected = self.detector.detect(raw_data)
            mapper = self.registry.get_mapper(detected.format)
            purchase = mapper.map(raw_data, source_file=path)
            purchase.detected_format = detected.format.value
            purchase.detection_confidence = detected.confidence
            validation = self.validator.validate(purchase, existing=existing)
            purchase.processing_warnings = [str(i) for i in validation.issues]
            if validation.is_valid:
                return purchase
            error_msgs = [
                str(e) for e in validation.issues if e.level == ValidationLevel.ERROR
            ]
            return {"file": path, "reason": "; ".join(error_msgs)}
        except MappingError as e:
            logger.warning("Mapping error for %s: %s", path, e)
            return {"file": path, "reason": str(e)}
        except JSONDecodeError as e:
            logger.warning("JSON error for %s: %s", path, e)
            return {"file": path, "reason": f"JSON invalido: {e}"}
        except Exception as e:
            logger.error("Unexpected error processing %s: %s", path, e)
            return {"file": path, "reason": str(e)}

    def _load_json(self, path: str) -> dict:
        """
        Load and parse a JSON file.
        Carga y parsea un archivo JSON.

        Args / Argumentos:
            path: Path to JSON file / Ruta al archivo JSON

        Returns / Retorna:
            Parsed JSON data / Datos JSON parseados

        Raises / Lanza:
            JSONDecodeError: If JSON is invalid
        """
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _count_formats(
        invoices: list[PurchaseInvoice],
    ) -> dict[str, int]:
        """
        Count detected formats in processed invoices.
        Cuenta formatos detectados en facturas procesadas.

        Args / Argumentos:
            invoices: List of processed invoices

        Returns / Retorna:
            Dict mapping format name to count
        """
        counts: dict[str, int] = {}
        for inv in invoices:
            fmt = inv.detected_format or "UNKNOWN"
            counts[fmt] = counts.get(fmt, 0) + 1
        return counts
