"""
JSON Processor / Procesador de JSON
===================================

Process and validate JSON invoice files.
Procesa y valida archivos JSON de facturas.

This module provides:
Este módulo provee:
- process_file: Process a single JSON file into an Invoice
                Procesa un archivo JSON en una Factura
- process_batch: Process multiple JSON files
                 Procesa múltiples archivos JSON
- validate_json_structure: Validate JSON structure before parsing
                           Valida estructura JSON antes de parsear
"""

import json
import logging
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from src.models.invoice import Invoice, InvoiceItem, InvoiceType

logger = logging.getLogger(__name__)


class JSONProcessorError(Exception):
    """
    Custom exception for JSON processing errors.
    Excepción personalizada para errores de procesamiento JSON.
    """

    def __init__(
        self,
        message: str,
        file_path: str | None = None,
        original_error: Exception | None = None,
    ) -> None:
        self.message = message
        self.file_path = file_path
        self.original_error = original_error
        super().__init__(self.message)


class JSONProcessor:
    """
    JSON invoice file processor / Procesador de archivos JSON de facturas.

    Processes JSON files containing invoice data and converts them to
    Invoice model objects with validation.

    Procesa archivos JSON con datos de facturas y los convierte en
    objetos del modelo Invoice con validación.

    Attributes / Atributos:
        required_fields: List of required fields in JSON
                         Lista de campos requeridos en JSON
        warnings: List of warnings generated during processing
                  Lista de advertencias generadas durante procesamiento
    """

    REQUIRED_FIELDS = ["document_number", "issue_date", "customer_name", "total"]
    OPTIONAL_FIELDS = ["invoice_type", "customer_id", "items", "subtotal", "tax"]

    def __init__(self) -> None:
        """
        Initialize the JSON processor.
        Inicializa el procesador JSON.
        """
        self.warnings: list[str] = []
        logger.debug("JSONProcessor initialized")

    def process_file(self, file_path: str) -> Invoice:
        """
        Process a single JSON file into an Invoice object.
        Procesa un archivo JSON individual en un objeto Invoice.

        Args / Argumentos:
            file_path: Path to the JSON file / Ruta al archivo JSON

        Returns / Retorna:
            Invoice object / Objeto Invoice

        Raises / Lanza:
            JSONProcessorError: If file cannot be processed
                                Si el archivo no puede ser procesado
        """
        self.warnings = []
        path = Path(file_path)

        logger.info("Processing JSON file: %s", file_path)

        if not path.exists():
            raise JSONProcessorError(
                f"File not found: {file_path}",
                file_path=file_path,
            )

        if not path.suffix.lower() == ".json":
            raise JSONProcessorError(
                f"Invalid file extension: {path.suffix}",
                file_path=file_path,
            )

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise JSONProcessorError(
                f"Invalid JSON format: {e}",
                file_path=file_path,
                original_error=e,
            ) from e
        except OSError as e:
            raise JSONProcessorError(
                f"Error reading file: {e}",
                file_path=file_path,
                original_error=e,
            ) from e

        if not self.validate_json_structure(data):
            raise JSONProcessorError(
                "Invalid JSON structure",
                file_path=file_path,
            )

        invoice = self._parse_invoice_data(data, file_path)
        logger.info("Successfully processed invoice: %s", invoice.document_number)

        return invoice

    def process_batch(
        self,
        file_paths: list[str],
        stop_on_error: bool = False,
    ) -> list[Invoice]:
        """
        Process multiple JSON files into Invoice objects.
        Procesa múltiples archivos JSON en objetos Invoice.

        Args / Argumentos:
            file_paths: List of paths to JSON files
                        Lista de rutas a archivos JSON
            stop_on_error: If True, stop on first error; otherwise continue
                           Si True, detiene en primer error; sino continúa

        Returns / Retorna:
            List of Invoice objects / Lista de objetos Invoice
        """
        invoices: list[Invoice] = []
        errors: list[tuple[str, str]] = []

        logger.info("Processing batch of %d JSON files", len(file_paths))

        for file_path in file_paths:
            try:
                invoice = self.process_file(file_path)
                invoices.append(invoice)
            except JSONProcessorError as e:
                errors.append((file_path, e.message))
                logger.error("Error processing %s: %s", file_path, e.message)

                if stop_on_error:
                    raise

        if errors:
            logger.warning(
                "Batch processing completed with %d errors out of %d files",
                len(errors),
                len(file_paths),
            )

        logger.info(
            "Batch processing complete: %d invoices processed successfully",
            len(invoices),
        )

        return invoices

    def validate_json_structure(self, data: dict[str, Any]) -> bool:
        """
        Validate that JSON data has the required structure.
        Valida que los datos JSON tengan la estructura requerida.

        Args / Argumentos:
            data: Dictionary of JSON data / Diccionario de datos JSON

        Returns / Retorna:
            True if structure is valid / True si la estructura es válida
        """
        if not isinstance(data, dict):
            logger.warning("JSON data is not a dictionary")
            return False

        missing_fields = []
        for field in self.REQUIRED_FIELDS:
            if field not in data:
                missing_fields.append(field)

        if missing_fields:
            self.warnings.append(
                f"Missing required fields: {', '.join(missing_fields)} / "
                f"Campos requeridos faltantes"
            )
            logger.warning("Missing required fields: %s", missing_fields)
            return False

        # Warn about missing optional fields
        for field in self.OPTIONAL_FIELDS:
            if field not in data:
                self.warnings.append(
                    f"Missing optional field: {field} / Campo opcional faltante"
                )
                logger.debug("Missing optional field: %s", field)

        return True

    def _parse_invoice_data(
        self,
        data: dict[str, Any],
        source_file: str,
    ) -> Invoice:
        """
        Parse JSON data into an Invoice object.
        Parsea datos JSON en un objeto Invoice.
        """
        # Parse items if present
        items = self._parse_items(data.get("items", []))

        # Calculate subtotal from items if not provided
        subtotal = self._parse_decimal(
            data.get("subtotal", sum(item.total for item in items) if items else 0)
        )

        # Parse invoice type
        invoice_type = self._parse_invoice_type(data.get("invoice_type", "factura"))

        invoice = Invoice(
            document_number=str(data["document_number"]),
            invoice_type=invoice_type,
            issue_date=data["issue_date"],
            customer_name=str(data["customer_name"]),
            customer_id=data.get("customer_id"),
            items=items,
            subtotal=subtotal,
            tax=self._parse_decimal(data.get("tax", 0)),
            total=self._parse_decimal(data["total"]),
            source_file=source_file,
        )

        return invoice

    def _parse_items(self, items_data: list[dict[str, Any]]) -> list[InvoiceItem]:
        """
        Parse item data into InvoiceItem objects.
        Parsea datos de ítems en objetos InvoiceItem.
        """
        items: list[InvoiceItem] = []

        for i, item_data in enumerate(items_data):
            try:
                item = InvoiceItem(
                    quantity=self._parse_decimal(item_data.get("quantity", 1)),
                    description=str(item_data.get("description", f"Item {i + 1}")),
                    unit_price=self._parse_decimal(item_data.get("unit_price", 0)),
                    total=self._parse_decimal(item_data.get("total", 0)),
                )
                items.append(item)
            except (ValueError, KeyError) as e:
                self.warnings.append(f"Error parsing item {i + 1}: {e}")
                logger.warning("Error parsing item %d: %s", i + 1, e)

        return items

    def _parse_invoice_type(self, type_str: str) -> InvoiceType:
        """
        Parse invoice type string to enum.
        Parsea string de tipo de factura a enum.
        """
        type_map = {
            "factura": InvoiceType.FACTURA,
            "invoice": InvoiceType.FACTURA,
            "ccf": InvoiceType.CCF,
            "credito_fiscal": InvoiceType.CCF,
            "nota_credito": InvoiceType.NOTA_CREDITO,
            "credit_note": InvoiceType.NOTA_CREDITO,
        }

        normalized = type_str.lower().strip()
        if normalized in type_map:
            return type_map[normalized]

        self.warnings.append(
            f"Unknown invoice type '{type_str}', defaulting to FACTURA"
        )
        logger.warning("Unknown invoice type: %s", type_str)
        return InvoiceType.FACTURA

    def _parse_decimal(self, value: Any) -> Decimal:
        """
        Parse value to Decimal, handling various input types.
        Parsea valor a Decimal, manejando varios tipos de entrada.
        """
        if isinstance(value, Decimal):
            return value

        try:
            if isinstance(value, (int, float)):
                return Decimal(str(value))
            if isinstance(value, str):
                return Decimal(value.replace(",", "."))
            return Decimal(str(value))
        except (InvalidOperation, ValueError) as e:
            logger.warning("Error parsing decimal value '%s': %s", value, e)
            return Decimal("0")

    def get_warnings(self) -> list[str]:
        """
        Get list of warnings from last processing operation.
        Obtiene lista de advertencias de la última operación.
        """
        return self.warnings.copy()

    def clear_warnings(self) -> None:
        """
        Clear the warnings list.
        Limpia la lista de advertencias.
        """
        self.warnings = []
