"""
Purchases Core Package / Paquete Core de Compras
=================================================

Core business logic for purchase invoice processing.
Logica de negocio central para el procesamiento de facturas de compra.

This package provides / Este paquete provee:
- FormatDetector: Intelligent format detection for JSON invoices
                  Deteccion inteligente de formato para facturas JSON
- DetectedFormat: Enum of recognized invoice formats
                  Enum de formatos de factura reconocidos
- DetectionResult: Result model for format detection
                   Modelo de resultado para deteccion de formato
"""

from src.core.purchases.format_detector import (
    DetectedFormat,
    DetectionResult,
    FormatDetector,
)

__all__ = [
    "DetectedFormat",
    "DetectionResult",
    "FormatDetector",
]
