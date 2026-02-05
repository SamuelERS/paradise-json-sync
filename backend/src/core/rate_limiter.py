"""
Rate Limiter Configuration / Configuración del Rate Limiter
============================================================

Centralized rate limiter that respects TESTING environment variable.
Rate limiter centralizado que respeta la variable de entorno TESTING.
"""

import os

from slowapi import Limiter
from slowapi.util import get_remote_address

# Detect testing mode / Detectar modo testing
TESTING = os.getenv("TESTING", "").lower() in ["true", "1", "test"]

# Rate limiter (disabled in testing mode)
# Rate limiter (deshabilitado en modo testing)
limiter = Limiter(key_func=get_remote_address, enabled=not TESTING)
