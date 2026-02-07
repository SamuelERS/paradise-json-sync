"""
Generic Fallback Mapper / Mapper Generico de Respaldo
=====================================================

Last-resort mapper that searches for fields using synonyms.
Mapper de ultimo recurso que busca campos usando sinonimos.

This module provides / Este modulo provee:
- GenericFallbackMapper: Fallback mapper using synonym table
                         Mapper de respaldo usando tabla de sinonimos
"""

import logging
from decimal import Decimal
from typing import Any, Optional

from src.core.purchases.base_mapper import BaseMapper, MappingError
from src.models.purchase_invoice import (
    PurchaseDocumentType,
    PurchaseInvoice,
    PurchaseInvoiceItem,
    SupplierInfo,
)

logger = logging.getLogger(__name__)


class GenericFallbackMapper(BaseMapper):
    """
    Last-resort mapper that searches fields by common names.
    Mapper de ultimo recurso que busca campos por nombres comunes.

    Uses a synonym table to find data in unknown JSON formats.
    Usa una tabla de sinonimos para encontrar datos en formatos
    JSON desconocidos.
    """

    FIELD_SYNONYMS: dict[str, list[str]] = {
        "document_number": [
            "codigoGeneracion", "codigo_generacion",
            "numero_factura", "invoice_number",
            "no_factura", "numero", "doc_number",
        ],
        "date": [
            "fecEmi", "fecha", "fecha_emision", "date",
            "issue_date", "fecha_factura", "invoice_date",
        ],
        "supplier_name": [
            "nombre_emisor", "emisor.nombre", "proveedor",
            "vendor", "supplier", "razon_social_emisor",
        ],
        "total": [
            "totalPagar", "total", "monto_total",
            "total_amount", "montoTotalOperacion",
            "totalAPagar", "grand_total",
        ],
        "items": [
            "cuerpoDocumento", "detalle", "items", "lineas",
            "productos", "lines", "line_items",
        ],
    }

    def can_handle(self, data: dict) -> bool:
        """
        Always returns True — this is the fallback.
        Siempre retorna True — este es el fallback.

        Args / Argumentos:
            data: JSON dictionary to check

        Returns / Retorna:
            Always True
        """
        return True

    def map(
        self, data: dict, source_file: str = "",
    ) -> PurchaseInvoice:
        """
        Map data by searching fields using synonyms.
        Mapea datos buscando campos usando sinonimos.

        Args / Argumentos:
            data: Raw JSON dictionary
            source_file: Source file path

        Returns / Retorna:
            PurchaseInvoice with found data

        Raises / Lanza:
            MappingError: If minimum fields not found
        """
        doc_number = self._find_field(data, "document_number")
        date_value = self._find_field(data, "date")
        total_value = self._find_field(data, "total")
        supplier_name = self._find_field(data, "supplier_name")
        items_data = self._find_field(data, "items")

        if not doc_number or total_value is None:
            raise MappingError(
                message=(
                    "No se pudieron extraer campos minimos"
                    " (numero, total)"
                ),
                source_file=source_file,
                partial_data={
                    "doc_number_found": doc_number is not None,
                    "total_found": total_value is not None,
                },
            )

        items = self._map_generic_items(items_data)
        total_dec = self._parse_decimal(total_value)

        supplier = SupplierInfo(
            name=str(supplier_name) if supplier_name else "Desconocido",
        )

        return PurchaseInvoice(
            document_number=str(doc_number),
            document_type=PurchaseDocumentType.DESCONOCIDO,
            issue_date=date_value if date_value else "2000-01-01",
            supplier=supplier,
            items=items,
            subtotal=total_dec,
            total=total_dec,
            source_file=source_file,
            raw_data=data,
        )

    def _find_field(
        self, data: dict, canonical_name: str,
    ) -> Any:
        """
        Search for a field in JSON using synonym table.
        Busca un campo en el JSON usando tabla de sinonimos.

        Supports nested keys with dot notation: "emisor.nombre"
        Soporta claves anidadas con notacion punto: "emisor.nombre"

        Args / Argumentos:
            data: JSON dictionary to search
            canonical_name: Canonical field name

        Returns / Retorna:
            Found value or None
        """
        synonyms = self.FIELD_SYNONYMS.get(canonical_name, [])
        for synonym in synonyms:
            if "." in synonym:
                parts = synonym.split(".")
                value = self._safe_get(data, *parts)
            else:
                value = data.get(synonym)
            if value is not None:
                return value
        return None

    def _map_generic_items(
        self, items_data: Any,
    ) -> list[PurchaseInvoiceItem]:
        """
        Map generic items list to PurchaseInvoiceItem list.
        Mapea lista generica de items a lista de PurchaseInvoiceItem.

        Args / Argumentos:
            items_data: List of item dicts or None

        Returns / Retorna:
            List of PurchaseInvoiceItem
        """
        if not items_data or not isinstance(items_data, list):
            return []

        items: list[PurchaseInvoiceItem] = []
        for idx, item in enumerate(items_data):
            if not isinstance(item, dict):
                continue
            items.append(self._map_single_generic_item(item, idx))
        return items

    def _map_single_generic_item(
        self, item: dict, idx: int,
    ) -> PurchaseInvoiceItem:
        """
        Map a single generic item dict to PurchaseInvoiceItem.
        Mapea un dict de item generico a PurchaseInvoiceItem.

        Args / Argumentos:
            item: Single item dictionary
            idx: Item index (0-based)

        Returns / Retorna:
            PurchaseInvoiceItem with mapped data
        """
        desc = (
            item.get("descripcion")
            or item.get("description")
            or item.get("producto")
            or item.get("nombre")
            or f"Item {idx + 1}"
        )
        qty = self._parse_decimal(
            item.get("cantidad")
            or item.get("quantity")
            or item.get("qty")
            or 1,
        )
        price = self._parse_decimal(
            item.get("precioUni")
            or item.get("unit_price")
            or item.get("precio")
            or 0,
        )
        total = self._parse_decimal(
            item.get("total")
            or item.get("monto")
            or item.get("amount")
            or 0,
        )
        if total == Decimal("0") and qty > 0 and price > 0:
            total = qty * price

        return PurchaseInvoiceItem(
            item_number=idx + 1,
            description=str(desc),
            quantity=qty if qty > 0 else Decimal("1"),
            unit_price=price,
            total=total,
        )
