"""
DTE Standard Mapper / Mapper DTE Estandar
==========================================

Mapper for the standard DTE format from Hacienda de El Salvador.
Mapper para el formato DTE estandar de Hacienda de El Salvador.

This module provides / Este modulo provee:
- DTEStandardMapper: Converts DTE standard JSON to PurchaseInvoice
                     Convierte JSON DTE estandar a PurchaseInvoice
"""

import logging
from decimal import Decimal
from typing import Optional

from src.core.purchases.base_mapper import BaseMapper, MappingError
from src.models.purchase_invoice import (
    PurchaseDocumentType,
    PurchaseInvoice,
    PurchaseInvoiceItem,
    SupplierInfo,
)

logger = logging.getLogger(__name__)

# Mapping of tipoDte codes to PurchaseDocumentType
# Mapeo de codigos tipoDte a PurchaseDocumentType
_TIPO_DTE_MAP: dict[str, PurchaseDocumentType] = {
    "01": PurchaseDocumentType.FACTURA,
    "03": PurchaseDocumentType.CCF,
    "05": PurchaseDocumentType.NOTA_CREDITO,
    "06": PurchaseDocumentType.NOTA_DEBITO,
    "07": PurchaseDocumentType.COMPROBANTE_RETENCION,
    "11": PurchaseDocumentType.FACTURA_EXPORTACION,
    "14": PurchaseDocumentType.SUJETO_EXCLUIDO,
    "15": PurchaseDocumentType.COMPROBANTE_DONACION,
}


class DTEStandardMapper(BaseMapper):
    """
    Mapper for DTE standard format from Hacienda.
    Mapper para formato DTE estandar de Hacienda.

    Expected structure / Estructura esperada:
    {
        "identificacion": { codigoGeneracion, tipoDte, fecEmi, ... },
        "emisor": { nit, nombre, nrc, ... },
        "receptor": { nombre, numDocumento, ... },
        "cuerpoDocumento": [ { numItem, descripcion, ... } ],
        "resumen": { totalPagar, totalIva, subTotal, ... },
        "apendice": [ ... ]  (optional)
    }

    NOTE: Similar to _normalize_dte_format in json_processor.py
    but adapted for PURCHASES perspective (emisor = supplier).
    NOTA: Similar a _normalize_dte_format en json_processor.py
    pero adaptado para perspectiva de COMPRAS (emisor = proveedor).
    """

    def can_handle(self, data: dict) -> bool:
        """
        Check if data has DTE standard structure.
        Verifica si los datos tienen estructura DTE estandar.

        Args / Argumentos:
            data: JSON dictionary to check

        Returns / Retorna:
            True if all required DTE keys are present
        """
        required = {
            "identificacion", "emisor", "receptor",
            "cuerpoDocumento", "resumen",
        }
        return required.issubset(data.keys())

    def map(
        self, data: dict, source_file: str = "",
    ) -> PurchaseInvoice:
        """
        Convert DTE standard JSON to PurchaseInvoice.
        Convierte JSON DTE estandar a PurchaseInvoice.

        Args / Argumentos:
            data: Raw DTE JSON dictionary
            source_file: Source file path

        Returns / Retorna:
            PurchaseInvoice with mapped data

        Raises / Lanza:
            MappingError: If critical fields are missing
        """
        try:
            return self._do_map(data, source_file)
        except MappingError:
            raise
        except Exception as e:
            raise MappingError(
                message=f"Error mapping DTE standard: {e}",
                source_file=source_file,
                partial_data={"raw_keys": list(data.keys())},
            ) from e

    def _do_map(
        self, data: dict, source_file: str,
    ) -> PurchaseInvoice:
        """
        Internal mapping logic.
        Logica interna de mapeo.
        """
        ident = data.get("identificacion", {})
        emisor = data.get("emisor", {})
        receptor = data.get("receptor", {})
        resumen = data.get("resumen", {})
        cuerpo = data.get("cuerpoDocumento", [])
        apendice = data.get("apendice")

        supplier = self._map_supplier(emisor)
        items = self._map_items(cuerpo)
        subtotal, tax, total = self._calculate_totals(
            resumen, items,
        )
        appendix = self._map_appendix(apendice)

        return PurchaseInvoice(
            document_number=ident.get("codigoGeneracion", ""),
            control_number=ident.get("numeroControl"),
            document_type=self._map_document_type(
                ident.get("tipoDte", "01"),
            ),
            issue_date=ident.get("fecEmi", ""),
            emission_time=ident.get("horEmi"),
            currency=ident.get("tipoMoneda", "USD"),
            dte_version=ident.get("version"),
            supplier=supplier,
            receiver_name=receptor.get("nombre"),
            receiver_nit=receptor.get("numDocumento"),
            receiver_nrc=receptor.get("nrc"),
            receiver_doc_type=receptor.get("tipoDocumento"),
            receiver_address=self._extract_address(
                receptor.get("direccion"),
            ),
            items=items,
            subtotal=subtotal,
            total_taxable=self._parse_decimal(
                resumen.get("totalGravada", 0),
            ),
            total_exempt=self._parse_decimal(
                resumen.get("totalExenta", 0),
            ),
            total_non_subject=self._parse_decimal(
                resumen.get("totalNoSuj", 0),
            ),
            total_discount=self._parse_decimal(
                resumen.get("totalDescu", 0),
            ),
            tax=tax,
            total=total,
            total_in_words=resumen.get("totalLetras"),
            payment_condition=resumen.get("condicionOperacion"),
            appendix_data=appendix,
            tax_seal=(
                data.get("SelloRecibido")
                or data.get("selloRecibido")
            ),
            source_file=source_file,
            raw_data=data,
        )

    def _map_supplier(self, emisor: dict) -> SupplierInfo:
        """
        Map emisor section to SupplierInfo.
        Mapea seccion emisor a SupplierInfo.

        In purchases, the ISSUER is our SUPPLIER.
        En compras, el EMISOR es nuestro PROVEEDOR.

        Args / Argumentos:
            emisor: Emisor dictionary from DTE

        Returns / Retorna:
            SupplierInfo with mapped data
        """
        return SupplierInfo(
            name=emisor.get("nombre", ""),
            commercial_name=emisor.get("nombreComercial"),
            nit=emisor.get("nit"),
            nrc=emisor.get("nrc"),
            economic_activity=emisor.get("descActividad"),
            address=self._extract_address(
                emisor.get("direccion"),
            ),
            phone=emisor.get("telefono"),
            email=emisor.get("correo"),
            establishment_code=emisor.get("codEstableMH"),
        )

    def _map_document_type(
        self, tipo_dte: str,
    ) -> PurchaseDocumentType:
        """
        Map tipoDte code to PurchaseDocumentType.
        Mapea codigo tipoDte a PurchaseDocumentType.

        Args / Argumentos:
            tipo_dte: DTE type code (01, 03, 05, etc.)

        Returns / Retorna:
            Corresponding PurchaseDocumentType
        """
        doc_type = _TIPO_DTE_MAP.get(
            tipo_dte, PurchaseDocumentType.DESCONOCIDO,
        )
        if doc_type == PurchaseDocumentType.DESCONOCIDO:
            logger.warning(
                "Unknown tipoDte '%s', using DESCONOCIDO",
                tipo_dte,
            )
        return doc_type

    def _map_items(
        self, cuerpo: list,
    ) -> list[PurchaseInvoiceItem]:
        """
        Map cuerpoDocumento to list of PurchaseInvoiceItem.
        Mapea cuerpoDocumento a lista de PurchaseInvoiceItem.

        Args / Argumentos:
            cuerpo: List of item dictionaries

        Returns / Retorna:
            List of PurchaseInvoiceItem
        """
        items: list[PurchaseInvoiceItem] = []
        if not cuerpo or not isinstance(cuerpo, list):
            return items

        for item_data in cuerpo:
            if not isinstance(item_data, dict):
                continue
            items.append(self._map_single_item(item_data))
        return items

    def _map_single_item(
        self, item_data: dict,
    ) -> PurchaseInvoiceItem:
        """
        Map a single cuerpoDocumento entry to PurchaseInvoiceItem.
        Mapea una entrada de cuerpoDocumento a PurchaseInvoiceItem.

        Args / Argumentos:
            item_data: Single item dictionary

        Returns / Retorna:
            PurchaseInvoiceItem with mapped data
        """
        quantity = self._parse_decimal(
            item_data.get("cantidad", 1),
        )
        unit_price = self._parse_decimal(
            item_data.get("precioUni", 0),
        )
        taxable_sale = self._parse_decimal(
            item_data.get("ventaGravada", 0),
        )
        exempt_sale = self._parse_decimal(
            item_data.get("ventaExenta", 0),
        )
        non_subject = self._parse_decimal(
            item_data.get("ventaNoSuj", 0),
        )
        discount = self._parse_decimal(
            item_data.get("montoDescu", 0),
        )
        item_tax = self._parse_decimal(
            item_data.get("ivaItem", 0),
        )

        item_total = taxable_sale + exempt_sale + non_subject
        if item_total == Decimal("0"):
            item_total = quantity * unit_price

        return PurchaseInvoiceItem(
            item_number=item_data.get("numItem"),
            product_code=item_data.get("codigo"),
            description=item_data.get("descripcion", ""),
            unit_measure=item_data.get("uniMedida"),
            quantity=quantity if quantity > 0 else Decimal("1"),
            unit_price=unit_price,
            original_price=self._parse_decimal(
                item_data.get("precioUni"),
            ) if item_data.get("precioUni") is not None else None,
            discount=discount,
            taxable_sale=taxable_sale,
            exempt_sale=exempt_sale,
            non_subject_sale=non_subject,
            item_tax=item_tax,
            total=item_total,
        )

    def _calculate_totals(
        self,
        resumen: dict,
        items: list[PurchaseInvoiceItem],
    ) -> tuple[Decimal, Decimal, Decimal]:
        """
        Calculate subtotal, tax, and total from resumen.
        Calcula subtotal, impuesto y total del resumen.

        Args / Argumentos:
            resumen: Resumen dictionary from DTE
            items: Mapped items list

        Returns / Retorna:
            Tuple of (subtotal, tax, total)
        """
        total = self._parse_decimal(
            resumen.get("totalPagar", 0),
        )
        tax = self._parse_decimal(
            resumen.get("totalIva", 0),
        )
        subtotal = self._parse_decimal(
            resumen.get("subTotal")
            or resumen.get("subTotalVentas")
            or resumen.get("totalGravada", 0),
        )

        if subtotal == Decimal("0") and total > Decimal("0"):
            subtotal = total - tax

        return subtotal, tax, total

    def _extract_address(
        self, direccion: Optional[dict | str],
    ) -> Optional[str]:
        """
        Extract address from dict or string.
        Extrae direccion de dict o string.

        Args / Argumentos:
            direccion: Address as dict or string

        Returns / Retorna:
            Address string or None
        """
        if direccion is None:
            return None
        if isinstance(direccion, str):
            return direccion
        if isinstance(direccion, dict):
            parts = []
            for key in (
                "complemento", "direccion",
                "municipio", "departamento",
            ):
                val = direccion.get(key)
                if val:
                    parts.append(str(val))
            return ", ".join(parts) if parts else None
        return None

    def _map_appendix(
        self, apendice: Optional[list],
    ) -> Optional[dict]:
        """
        Map appendix data to dict.
        Mapea datos de apendice a dict.

        Args / Argumentos:
            apendice: Appendix list or None

        Returns / Retorna:
            Dict with appendix entries or None
        """
        if not apendice:
            return None
        if isinstance(apendice, list):
            return {"entries": apendice}
        if isinstance(apendice, dict):
            return apendice
        return None
