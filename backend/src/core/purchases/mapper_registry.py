"""
Mapper Registry / Registro de Mappers
======================================

Central registry that associates DetectedFormat with its mapper.
Registro central que asocia DetectedFormat con su mapper.

This module provides / Este modulo provee:
- MapperNotFoundError: Error when no mapper is found
                       Error cuando no se encuentra mapper
- MapperRegistry: Central mapper registry
                  Registro central de mappers
- create_default_registry: Factory function for default registry
                           Funcion fabrica para registry predeterminado
"""

import logging
from typing import Optional

from src.core.purchases.base_mapper import BaseMapper
from src.core.purchases.format_detector import DetectedFormat

logger = logging.getLogger(__name__)


class MapperNotFoundError(Exception):
    """
    Error when no mapper is found for a format.
    Error cuando no se encuentra mapper para un formato.
    """

    pass


class MapperRegistry:
    """
    Central mapper registry.
    Registro central de mappers.

    Associates each DetectedFormat with its corresponding mapper.
    Asocia cada DetectedFormat con su mapper correspondiente.
    """

    def __init__(self) -> None:
        """
        Initialize empty registry.
        Inicializa registro vacio.
        """
        self._mappers: dict[DetectedFormat, BaseMapper] = {}
        self._fallback: Optional[BaseMapper] = None

    def register(
        self,
        format_type: DetectedFormat,
        mapper: BaseMapper,
    ) -> None:
        """
        Register a mapper for a specific format.
        Registra un mapper para un formato especifico.

        Args / Argumentos:
            format_type: The format to register for
            mapper: The mapper instance to use
        """
        self._mappers[format_type] = mapper
        logger.info(
            "Registered mapper for format: %s",
            format_type.value,
        )

    def set_fallback(self, mapper: BaseMapper) -> None:
        """
        Set the fallback mapper for unknown formats.
        Define el mapper de fallback para formatos desconocidos.

        Args / Argumentos:
            mapper: The fallback mapper instance
        """
        self._fallback = mapper
        logger.info("Set fallback mapper: %s", type(mapper).__name__)

    def get_mapper(
        self, format_type: DetectedFormat,
    ) -> BaseMapper:
        """
        Get the mapper for a format. Falls back if not found.
        Obtiene el mapper para un formato. Usa fallback si no existe.

        Args / Argumentos:
            format_type: The format to get a mapper for

        Returns / Retorna:
            The mapper for the given format

        Raises / Lanza:
            MapperNotFoundError: If no mapper and no fallback
        """
        if format_type in self._mappers:
            return self._mappers[format_type]
        if self._fallback is not None:
            logger.info(
                "No mapper for %s, using fallback",
                format_type.value,
            )
            return self._fallback
        raise MapperNotFoundError(
            f"No mapper registered for {format_type.value}"
        )

    def list_formats(self) -> list[DetectedFormat]:
        """
        List all registered formats (excluding fallback).
        Lista todos los formatos registrados (sin fallback).

        Returns / Retorna:
            List of registered DetectedFormat values
        """
        return list(self._mappers.keys())


def create_default_registry() -> MapperRegistry:
    """
    Create the registry with default mappers.
    Crea el registry con mappers predeterminados.

    Registers DTE_STANDARD and sets GenericFallback as fallback.
    Only these two mappers are available until real provider data
    is analyzed for VARIANT_A, VARIANT_B, etc.

    Registra DTE_STANDARD y establece GenericFallback como fallback.
    Solo estos dos mappers estan disponibles hasta que se analicen
    datos reales de proveedores para VARIANT_A, VARIANT_B, etc.

    Returns / Retorna:
        MapperRegistry with default configuration
    """
    from src.core.purchases.mappers.dte_standard import (
        DTEStandardMapper,
    )
    from src.core.purchases.mappers.generic_fallback import (
        GenericFallbackMapper,
    )

    registry = MapperRegistry()
    registry.register(
        DetectedFormat.DTE_STANDARD, DTEStandardMapper(),
    )
    registry.set_fallback(GenericFallbackMapper())
    return registry
