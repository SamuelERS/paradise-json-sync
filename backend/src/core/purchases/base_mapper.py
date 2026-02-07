"""
Base Mapper / Mapper Base
=========================

Abstract base class for all purchase invoice format mappers.
Clase base abstracta para todos los mappers de formato de facturas de compra.

This module provides / Este modulo provee:
- BaseMapper: Abstract class defining the mapper contract
               Clase abstracta que define el contrato de mappers
- MappingError: Exception for mapping failures
                Excepcion para fallos de mapeo
"""

import logging
from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

logger = logging.getLogger(__name__)


class MappingError(Exception):
    """
    Error during format mapping to canonical model.
    Error durante el mapeo de un formato al modelo canonico.

    Attributes / Atributos:
        message: Error description / Descripcion del error
        source_file: Source file path / Ruta del archivo fuente
        partial_data: Partially extracted data / Datos parciales extraidos
    """

    def __init__(
        self,
        message: str,
        source_file: str = "",
        partial_data: Optional[dict] = None,
    ) -> None:
        self.message = message
        self.source_file = source_file
        self.partial_data = partial_data
        super().__init__(message)


class BaseMapper(ABC):
    """
    Abstract base class for all format mappers.
    Clase base abstracta para todos los mappers de formato.

    Each mapper converts a specific JSON format to PurchaseInvoice.
    Cada mapper convierte un formato JSON especifico a PurchaseInvoice.
    """

    @abstractmethod
    def map(self, data: dict, source_file: str = "") -> Any:
        """
        Convert raw JSON data to PurchaseInvoice.
        Convierte datos JSON crudos a PurchaseInvoice.

        Args / Argumentos:
            data: Raw JSON dictionary / Diccionario JSON crudo
            source_file: Source file path / Ruta del archivo fuente

        Returns / Retorna:
            PurchaseInvoice normalized / PurchaseInvoice normalizado

        Raises / Lanza:
            MappingError: If conversion fails / Si la conversion falla
        """
        pass

    @abstractmethod
    def can_handle(self, data: dict) -> bool:
        """
        Check if this mapper can handle the given data.
        Verifica si este mapper puede manejar los datos dados.

        Args / Argumentos:
            data: JSON dictionary to check / Diccionario JSON a verificar

        Returns / Retorna:
            True if this mapper can handle the data
        """
        pass

    def _parse_decimal(self, value: Any) -> Decimal:
        """
        Safely convert a value to Decimal.
        Convierte un valor a Decimal de forma segura.

        Handles: None, str, int, float, Decimal.
        Maneja: None, str, int, float, Decimal.

        Args / Argumentos:
            value: Value to convert / Valor a convertir

        Returns / Retorna:
            Decimal representation / Representacion Decimal
        """
        if value is None:
            return Decimal("0")
        if isinstance(value, Decimal):
            return value
        try:
            if isinstance(value, (int, float)):
                return Decimal(str(value))
            if isinstance(value, str):
                return Decimal(value.replace(",", "."))
            return Decimal(str(value))
        except (InvalidOperation, ValueError) as e:
            logger.warning(
                "Error parsing decimal value '%s': %s", value, e,
            )
            return Decimal("0")

    def _parse_date(self, value: Any) -> Optional[date]:
        """
        Parse date from multiple formats.
        Parsea fecha de multiples formatos.

        Formats / Formatos: %Y-%m-%d, %d/%m/%Y, %d-%m-%Y

        Args / Argumentos:
            value: Value to parse / Valor a parsear

        Returns / Retorna:
            Parsed date or None / Fecha parseada o None
        """
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
            logger.warning("Could not parse date: '%s'", value)
        return None

    def _safe_get(
        self,
        data: dict,
        *keys: str,
        default: Any = None,
    ) -> Any:
        """
        Safe access to nested dictionary keys.
        Acceso seguro a claves anidadas de diccionario.

        Example / Ejemplo:
            _safe_get(data, "resumen", "totalPagar", default=0)

        Args / Argumentos:
            data: Dictionary to traverse / Diccionario a recorrer
            *keys: Key path / Ruta de claves
            default: Default value if key not found

        Returns / Retorna:
            Found value or default / Valor encontrado o default
        """
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
