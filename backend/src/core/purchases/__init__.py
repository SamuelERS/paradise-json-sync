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
- BaseMapper: Abstract base class for format mappers
              Clase base abstracta para mappers de formato
- MappingError: Exception for mapping failures
                Excepcion para fallos de mapeo
- MapperRegistry: Central mapper registry
                  Registro central de mappers
- MapperNotFoundError: Error when no mapper found
                       Error cuando no se encuentra mapper
- create_default_registry: Factory for default registry
                           Fabrica para registry predeterminado
- DTEStandardMapper: Mapper for DTE standard format
                     Mapper para formato DTE estandar
- GenericFallbackMapper: Fallback mapper using synonyms
                         Mapper de respaldo usando sinonimos
- PDFExtractedMapper: Mapper for PDF-extracted invoice data
                      Mapper para datos de factura extraidos de PDF
- PDFExtractor: Extract data from digital PDF invoices
                Extrae datos de facturas PDF digitales
- PDFExtractionError: Exception for PDF extraction failures
                      Excepcion para fallos de extraccion de PDF
- PurchaseValidator: Purchase invoice validator
                     Validador de facturas de compra
- ValidationResult: Validation result model
                    Modelo de resultado de validacion
- ValidationIssue: Individual validation issue model
                   Modelo de problema de validacion individual
- ValidationLevel: Severity level enum
                   Enum de nivel de severidad
"""

from src.core.purchases.base_mapper import BaseMapper, MappingError
from src.core.purchases.format_detector import (
    DetectedFormat,
    DetectionResult,
    FormatDetector,
)
from src.core.purchases.mapper_registry import (
    MapperNotFoundError,
    MapperRegistry,
    create_default_registry,
)
from src.core.purchases.mappers.dte_standard import DTEStandardMapper
from src.core.purchases.mappers.generic_fallback import (
    GenericFallbackMapper,
)
from src.core.purchases.mappers.pdf_extracted import PDFExtractedMapper
from src.core.purchases.pdf_extractor import PDFExtractionError, PDFExtractor
from src.core.purchases.purchase_exporter import PurchaseExporter
from src.core.purchases.validator import (
    PurchaseValidator,
    ValidationIssue,
    ValidationLevel,
    ValidationResult,
)

__all__ = [
    "BaseMapper",
    "DetectedFormat",
    "DetectionResult",
    "DTEStandardMapper",
    "FormatDetector",
    "GenericFallbackMapper",
    "MapperNotFoundError",
    "MapperRegistry",
    "MappingError",
    "PDFExtractionError",
    "PDFExtractedMapper",
    "PDFExtractor",
    "PurchaseExporter",
    "PurchaseValidator",
    "ValidationIssue",
    "ValidationLevel",
    "ValidationResult",
    "create_default_registry",
]
