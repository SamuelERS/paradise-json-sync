"""
Mappers Package / Paquete de Mappers
=====================================

Concrete mapper implementations for purchase invoice formats.
Implementaciones concretas de mappers para formatos de facturas de compra.

This package provides / Este paquete provee:
- DTEStandardMapper: Mapper for DTE standard format (Hacienda)
                     Mapper para formato DTE estandar (Hacienda)
- GenericFallbackMapper: Fallback mapper using field synonyms
                         Mapper de respaldo usando sinonimos de campos
"""

from src.core.purchases.mappers.dte_standard import DTEStandardMapper
from src.core.purchases.mappers.generic_fallback import (
    GenericFallbackMapper,
)

__all__ = [
    "DTEStandardMapper",
    "GenericFallbackMapper",
]
