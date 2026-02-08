"""
PDF Extracted Mapper / Mapper de PDF Extraido
==============================================

Mapper for invoice data extracted from digital PDF files.
Mapper para datos de factura extraidos de archivos PDF digitales.

This module provides / Este modulo provee:
- PDFExtractedMapper: Converts PDF-extracted data to PurchaseInvoice
                      Convierte datos extraidos de PDF a PurchaseInvoice

Handles partial data — many fields may be missing from PDF extraction.
Maneja datos parciales — muchos campos pueden faltar de la extraccion PDF.
"""

import logging
from datetime import date
from pathlib import Path

from src.core.purchases.base_mapper import BaseMapper, MappingError
from src.models.purchase_invoice import (
    PurchaseDocumentType,
    PurchaseInvoice,
    SupplierInfo,
)

logger = logging.getLogger(__name__)


class PDFExtractedMapper(BaseMapper):
    """
    Mapper for PDF-extracted invoice data.
    Mapper para datos de factura extraidos de PDF.

    Handles partial data — many fields may be missing from extraction.
    Maneja datos parciales — muchos campos pueden faltar de la extraccion.

    Always sets document_type to DESCONOCIDO and adds a processing
    warning requiring manual verification.
    Siempre establece document_type como DESCONOCIDO y agrega una
    advertencia de procesamiento que requiere verificacion manual.
    """

    def can_handle(self, data: dict) -> bool:
        """
        Check for _extracted_from_pdf flag.
        Verifica flag de extraccion de PDF.

        Args / Argumentos:
            data: Dictionary to check / Diccionario a verificar

        Returns / Retorna:
            True if data was extracted from PDF
        """
        return data.get("_extracted_from_pdf", False) is True

    def map(
        self, data: dict, source_file: str = "",
    ) -> PurchaseInvoice:
        """
        Create PurchaseInvoice from PDF-extracted data.
        Crea PurchaseInvoice desde datos extraidos de PDF.

        Missing fields get defaults. Always adds processing warning.
        Campos faltantes obtienen defaults. Siempre agrega advertencia.

        Args / Argumentos:
            data: PDF-extracted data dict / Dict de datos extraidos de PDF
            source_file: Source file path / Ruta del archivo fuente

        Returns / Retorna:
            PurchaseInvoice with mapped data / PurchaseInvoice con datos mapeados

        Raises / Lanza:
            MappingError: If mapping fails / Si el mapeo falla
        """
        try:
            return self._do_map(data, source_file)
        except MappingError:
            raise
        except Exception as e:
            raise MappingError(
                message=f"Error mapping PDF data: {e}",
                source_file=source_file,
                partial_data=data,
            ) from e

    def _do_map(
        self, data: dict, source_file: str,
    ) -> PurchaseInvoice:
        """
        Internal mapping logic.
        Logica interna de mapeo.

        Args / Argumentos:
            data: PDF-extracted data / Datos extraidos de PDF
            source_file: Source file path / Ruta del archivo fuente

        Returns / Retorna:
            PurchaseInvoice instance
        """
        doc_number = data.get("document_number")
        if not doc_number:
            stem = Path(source_file).stem if source_file else "unknown"
            doc_number = f"PDF-{stem}"

        supplier = SupplierInfo(
            name=data.get("supplier_name") or "Proveedor Desconocido",
            nit=data.get("supplier_nit"),
            nrc=data.get("supplier_nrc"),
        )

        issue_date = self._parse_date(data.get("issue_date"))
        if issue_date is None:
            issue_date = date.today()

        fields_found = data.get("_extraction_fields_found", [])

        return PurchaseInvoice(
            document_number=doc_number,
            control_number=data.get("control_number"),
            document_type=PurchaseDocumentType.DESCONOCIDO,
            issue_date=issue_date,
            supplier=supplier,
            subtotal=self._parse_decimal(data.get("subtotal", 0)),
            tax=self._parse_decimal(data.get("tax", 0)),
            total=self._parse_decimal(data.get("total", 0)),
            items=[],
            source_file=source_file,
            detected_format="PDF_EXTRACTED",
            detection_confidence=0.5,
            raw_data=None,
            processing_warnings=[
                "Datos extraídos de PDF — verificar manualmente",
                f"Campos encontrados: {fields_found}",
            ],
        )
