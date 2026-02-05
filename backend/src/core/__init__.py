"""
Core Processing Modules / Módulos de Procesamiento Central
=========================================================

This package contains the core processing logic:
Este paquete contiene la lógica central de procesamiento:

- JSONProcessor: Process and validate JSON invoice files
                 Procesa y valida archivos JSON de facturas
- PDFProcessor: Merge and validate PDF documents
                Une y valida documentos PDF
- ExcelExporter: Export invoice data to Excel format
                 Exporta datos de facturas a formato Excel
- DataValidator: Validate invoice data integrity
                 Valida la integridad de datos de facturas
"""

from src.core.data_validator import DataValidator
from src.core.excel_exporter import ExcelExporter
from src.core.json_processor import JSONProcessor
from src.core.pdf_processor import PDFProcessor

__all__ = [
    "JSONProcessor",
    "PDFProcessor",
    "ExcelExporter",
    "DataValidator",
]
