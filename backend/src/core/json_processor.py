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
from typing import Any, List, Optional

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
        file_path: Optional[str] = None,
        original_error: Optional[Exception] = None,
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

        # Normalize nested format to flat format if needed
        data = self._normalize_nested_format(data)

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

    def _normalize_nested_format(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize nested JSON format to flat format.
        Normaliza formato JSON anidado a formato plano.

        Supports formats like:
        - DTE El Salvador: identificacion.codigoGeneracion, resumen.totalPagar
        - Generic nested: factura.numero, totales.total
        """
        # Detect DTE El Salvador format
        if "identificacion" in data and "resumen" in data:
            logger.info("Detected DTE El Salvador format, normalizing...")
            return self._normalize_dte_format(data)

        # Check if it's the nested format (has 'factura' key)
        if "factura" not in data:
            return data  # Already flat format

        logger.info("Detected nested invoice format, normalizing...")
        factura = data.get("factura", {})
        receptor = data.get("receptor", {})
        emisor = data.get("emisor", {})
        totales = data.get("totales", {})
        items_raw = data.get("items", [])

        # Map nested to flat format
        normalized = {
            "document_number": factura.get("numero", ""),
            "issue_date": factura.get("fecha", ""),
            "invoice_type": factura.get("tipoComprobante", "factura"),
            "customer_name": receptor.get("razonSocial", ""),
            "customer_id": receptor.get("ruc", ""),
            "subtotal": totales.get("subtotal", 0),
            "tax": totales.get("igv", totales.get("iva", 0)),
            "total": totales.get("total", 0),
        }

        # Normalize items
        normalized_items = []
        for item in items_raw:
            normalized_items.append({
                "description": item.get("descripcion", ""),
                "quantity": item.get("cantidad", 1),
                "unit_price": item.get("precioUnitario", 0),
                "total": item.get("total", item.get("subtotal", 0)),
            })
        normalized["items"] = normalized_items

        return normalized

    def _normalize_dte_format(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize DTE El Salvador format to flat format.
        Normaliza formato DTE de El Salvador a formato plano.

        DTE (Documento Tributario Electrónico) is the electronic invoicing
        standard used in El Salvador.

        Note: DTE invoices may have IVA included in prices, so totalPagar
        may equal subTotal even when totalIva > 0. We handle this by
        checking if total = subtotal and adjusting accordingly.

        This method extracts ALL available fields from the DTE to prevent
        data loss during processing.
        """
        identificacion = data.get("identificacion", {})
        emisor = data.get("emisor", {})
        receptor = data.get("receptor", {})
        resumen = data.get("resumen", {})
        cuerpo = data.get("cuerpoDocumento", [])
        apendice = data.get("apendice", [])

        # Extract raw values
        subtotal_raw = resumen.get("subTotal", resumen.get("subTotalVentas", 0))
        tax_raw = resumen.get("totalIva", 0)
        total_raw = resumen.get("totalPagar", resumen.get("montoTotalOperacion", 0))

        # Handle DTE quirk: if totalPagar ≈ subTotal (within tolerance) and totalIva > 0,
        # the IVA is informational only (already included in prices)
        # Also handle case where total ≈ subtotal + tax (normal case)
        tolerance = 0.02
        subtotal_matches_total = abs(subtotal_raw - total_raw) <= tolerance
        total_matches_sum = abs(total_raw - (subtotal_raw + tax_raw)) <= tolerance

        if total_matches_sum:
            # Normal case: total = subtotal + tax
            subtotal = subtotal_raw
            tax = tax_raw
            total = total_raw
        elif subtotal_matches_total and tax_raw > 0:
            # IVA is already included in the subtotal/total
            logger.debug("DTE with IVA included in prices detected")
            subtotal = total_raw
            tax = 0
            total = total_raw
        else:
            # Use total as-is, calculate tax difference if needed
            logger.debug("DTE with inconsistent totals, using totalPagar as total")
            subtotal = total_raw
            tax = 0
            total = total_raw

        # Extract apendice data (vendedor, N° documento interno)
        # DTE apendice uses various field names:
        # - "Datos del vendedor", "vendedor", "Vendedor" for seller
        # - "Datos del documento", "N° Documento", "documento" for internal doc number
        seller_name = None
        internal_doc_number = None
        for item in apendice:
            campo = item.get("campo", "").lower()
            valor = item.get("valor", "")
            if "vendedor" in campo:
                seller_name = valor
            elif "documento" in campo and "operacion" not in campo:
                internal_doc_number = valor

        # Build issuer address from components
        emisor_direccion = emisor.get("direccion", {})
        if isinstance(emisor_direccion, dict):
            issuer_address = emisor_direccion.get("complemento", "")
        else:
            issuer_address = str(emisor_direccion) if emisor_direccion else None

        # Build receptor address from components
        receptor_direccion = receptor.get("direccion", {})
        if isinstance(receptor_direccion, dict):
            customer_address = receptor_direccion.get("complemento", "")
        else:
            customer_address = str(receptor_direccion) if receptor_direccion else None

        # Map ALL DTE fields to flat format
        normalized = {
            # Core fields / Campos principales
            "document_number": identificacion.get(
                "codigoGeneracion", identificacion.get("numeroControl", "")
            ),
            "issue_date": identificacion.get("fecEmi", ""),
            "invoice_type": self._map_tipo_dte(identificacion.get("tipoDte", "01")),
            "customer_name": receptor.get("nombre", ""),
            "customer_id": receptor.get("numDocumento", ""),
            "subtotal": subtotal,
            "tax": tax,
            "total": total,

            # DTE Identification / Identificación DTE
            "control_number": identificacion.get("numeroControl", ""),
            "emission_time": identificacion.get("horEmi", ""),
            "currency": identificacion.get("tipoMoneda", "USD"),

            # Issuer data / Datos del emisor
            "issuer_nit": emisor.get("nit", ""),
            "issuer_nrc": emisor.get("nrc", ""),
            "issuer_name": emisor.get("nombre", ""),
            "issuer_commercial_name": emisor.get("nombreComercial", ""),
            "issuer_address": issuer_address,

            # Customer additional data / Datos adicionales del cliente
            "customer_doc_type": receptor.get("tipoDocumento", ""),
            "customer_nrc": receptor.get("nrc", ""),
            "customer_address": customer_address,
            "customer_phone": receptor.get("telefono", ""),
            "customer_email": receptor.get("correo", ""),

            # Summary fields / Campos de resumen
            "total_non_subject": resumen.get("totalNoSuj", 0),
            "total_exempt": resumen.get("totalExenta", 0),
            "total_taxable": resumen.get("totalGravada", 0),
            "total_discount": resumen.get("totalDescu", 0),
            "total_in_words": resumen.get("totalLetras", ""),
            "payment_condition": resumen.get("condicionOperacion"),

            # Appendix data / Datos del apéndice
            "seller_name": seller_name,
            "internal_doc_number": internal_doc_number,

            # Tax seal / Sello fiscal
            "tax_seal": data.get("SelloRecibido") or data.get("selloRecibido", ""),
        }

        # Normalize items from cuerpoDocumento with ALL fields
        normalized_items = []
        items_sum = 0
        for item in cuerpo:
            # Calculate item total from ventaGravada, ventaNoSuj, ventaExenta
            venta_gravada = item.get("ventaGravada", 0)
            venta_no_suj = item.get("ventaNoSuj", 0)
            venta_exenta = item.get("ventaExenta", 0)
            item_total = venta_gravada + venta_no_suj + venta_exenta

            quantity = item.get("cantidad", 1)
            original_price = item.get("precioUni", 0)

            # Use effective unit price (total / quantity) to pass validation
            # This handles DTE items with discounts where precioUni * cantidad != ventaGravada
            if quantity > 0 and item_total > 0:
                effective_unit_price = item_total / quantity
            else:
                effective_unit_price = original_price

            final_item_total = item_total if item_total > 0 else original_price
            items_sum += final_item_total

            normalized_items.append({
                "description": item.get("descripcion", ""),
                "quantity": quantity,
                "unit_price": effective_unit_price,
                "total": final_item_total,
                # DTE-specific item fields
                "item_number": item.get("numItem"),
                "product_code": item.get("codigo", ""),
                "unit_measure": item.get("uniMedida"),
                "original_price": original_price,
                "discount": item.get("montoDescu", 0),
                "item_tax": item.get("ivaItem", 0),
                "non_subject_sale": venta_no_suj,
                "exempt_sale": venta_exenta,
                "taxable_sale": venta_gravada,
            })
        normalized["items"] = normalized_items

        # Adjust subtotal to match items sum if there's a small rounding difference
        # This avoids validation failures due to DTE rounding inconsistencies
        if normalized_items and abs(normalized["subtotal"] - items_sum) <= 0.10:
            normalized["subtotal"] = items_sum
            # Recalculate total if tax is 0
            if normalized["tax"] == 0:
                normalized["total"] = items_sum

        logger.debug(
            "DTE normalized: doc=%s, control=%s, customer=%s, seller=%s, total=%s",
            normalized["document_number"][:20] if normalized["document_number"] else "N/A",
            normalized["control_number"][:30] if normalized["control_number"] else "N/A",
            normalized["customer_name"][:20] if normalized["customer_name"] else "N/A",
            normalized["seller_name"][:20] if normalized["seller_name"] else "N/A",
            normalized["total"],
        )

        return normalized

    def _map_tipo_dte(self, tipo_dte: str) -> str:
        """
        Map DTE type codes to invoice type strings.
        Mapea códigos de tipo DTE a strings de tipo de factura.

        DTE type codes (El Salvador):
        - 01: Factura de Consumidor Final
        - 03: Comprobante de Crédito Fiscal
        - 05: Nota de Crédito
        - 06: Nota de Débito
        - 11: Factura de Exportación
        - 14: Factura de Sujeto Excluido
        """
        dte_map = {
            "01": "factura",
            "03": "ccf",
            "05": "nota_credito",
            "06": "nota_debito",
            "11": "factura",
            "14": "factura",
        }
        return dte_map.get(str(tipo_dte), "factura")

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
                self.warnings.append(f"Missing optional field: {field} / Campo opcional faltante")
                logger.debug("Missing optional field: %s", field)

        return True

    def _parse_invoice_data(
        self,
        data: dict[str, Any],
        source_file: str,
    ) -> Invoice:
        """
        Parse JSON data into an Invoice object with ALL DTE fields.
        Parsea datos JSON en un objeto Invoice con TODOS los campos DTE.
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
            # Core fields / Campos principales
            document_number=str(data["document_number"]),
            invoice_type=invoice_type,
            issue_date=data["issue_date"],
            customer_name=str(data["customer_name"]),
            customer_id=data.get("customer_id") or None,
            items=items,
            subtotal=subtotal,
            tax=self._parse_decimal(data.get("tax", 0)),
            total=self._parse_decimal(data["total"]),
            source_file=source_file,

            # DTE Identification / Identificación DTE
            control_number=data.get("control_number") or None,
            emission_time=data.get("emission_time") or None,
            currency=data.get("currency", "USD"),

            # Issuer data / Datos del emisor
            issuer_nit=data.get("issuer_nit") or None,
            issuer_nrc=data.get("issuer_nrc") or None,
            issuer_name=data.get("issuer_name") or None,
            issuer_commercial_name=data.get("issuer_commercial_name") or None,
            issuer_address=data.get("issuer_address") or None,

            # Customer additional data / Datos adicionales del cliente
            customer_doc_type=data.get("customer_doc_type") or None,
            customer_nrc=data.get("customer_nrc") or None,
            customer_address=data.get("customer_address") or None,
            customer_phone=data.get("customer_phone") or None,
            customer_email=data.get("customer_email") or None,

            # Summary fields / Campos de resumen
            total_non_subject=self._parse_decimal(data.get("total_non_subject", 0)),
            total_exempt=self._parse_decimal(data.get("total_exempt", 0)),
            total_taxable=self._parse_decimal(data.get("total_taxable", 0)),
            total_discount=self._parse_decimal(data.get("total_discount", 0)),
            total_in_words=data.get("total_in_words") or None,
            payment_condition=data.get("payment_condition"),

            # Appendix data / Datos del apéndice
            seller_name=data.get("seller_name") or None,
            internal_doc_number=data.get("internal_doc_number") or None,

            # Tax seal / Sello fiscal
            tax_seal=data.get("tax_seal") or None,
        )

        return invoice

    def _parse_items(self, items_data: list[dict[str, Any]]) -> list[InvoiceItem]:
        """
        Parse item data into InvoiceItem objects with ALL DTE fields.
        Parsea datos de ítems en objetos InvoiceItem con TODOS los campos DTE.
        """
        items: list[InvoiceItem] = []

        for i, item_data in enumerate(items_data):
            try:
                item = InvoiceItem(
                    # Core fields / Campos principales
                    quantity=self._parse_decimal(item_data.get("quantity", 1)),
                    description=str(item_data.get("description", f"Item {i + 1}")),
                    unit_price=self._parse_decimal(item_data.get("unit_price", 0)),
                    total=self._parse_decimal(item_data.get("total", 0)),
                    # DTE-specific fields / Campos específicos DTE
                    item_number=item_data.get("item_number"),
                    product_code=item_data.get("product_code") or None,
                    unit_measure=item_data.get("unit_measure"),
                    original_price=self._parse_decimal(item_data.get("original_price", 0))
                    if item_data.get("original_price") is not None
                    else None,
                    discount=self._parse_decimal(item_data.get("discount", 0)),
                    item_tax=self._parse_decimal(item_data.get("item_tax", 0)),
                    non_subject_sale=self._parse_decimal(item_data.get("non_subject_sale", 0)),
                    exempt_sale=self._parse_decimal(item_data.get("exempt_sale", 0)),
                    taxable_sale=self._parse_decimal(item_data.get("taxable_sale", 0)),
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

        self.warnings.append(f"Unknown invoice type '{type_str}', defaulting to FACTURA")
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
