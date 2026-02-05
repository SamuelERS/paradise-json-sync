"""
Multipart Form Configuration / Configuración de Formularios Multipart
======================================================================

This module patches Starlette's Request class to support bulk file uploads
beyond the default limit of 1000 files.

Este módulo parchea la clase Request de Starlette para soportar uploads
masivos de archivos más allá del límite predeterminado de 1000 archivos.

Configuration:
- MAX_UPLOAD_FILES: Maximum number of files per upload (default: 10000)
- MAX_UPLOAD_FIELDS: Maximum number of form fields (default: 10000)

Configuración:
- MAX_UPLOAD_FILES: Número máximo de archivos por upload (predeterminado: 10000)
- MAX_UPLOAD_FIELDS: Número máximo de campos de formulario (predeterminado: 10000)

Security Note / Nota de Seguridad:
The default Starlette limit of 1000 files exists to prevent DoS attacks.
Increase this limit only if you have proper rate limiting in place.

El límite predeterminado de 1000 archivos de Starlette existe para prevenir
ataques DoS. Aumenta este límite solo si tienes un rate limiting adecuado.
"""

import os
from starlette import requests as starlette_requests

# Configuration from environment or defaults
# Configuración desde entorno o valores predeterminados
MAX_UPLOAD_FILES = int(os.getenv("MAX_UPLOAD_FILES", "10000"))
MAX_UPLOAD_FIELDS = int(os.getenv("MAX_UPLOAD_FIELDS", "10000"))

# Store original __init__ method
_original_request_init = starlette_requests.Request.__init__


def _patched_request_init(self, *args, **kwargs):
    """
    Patched Request.__init__ that overrides the form method with custom limits.
    __init__ parcheado que sobrescribe el método form con límites personalizados.
    """
    _original_request_init(self, *args, **kwargs)

    # Store reference to original form method bound to this instance
    original_form = self.form

    async def custom_form(
        max_files: int = MAX_UPLOAD_FILES,
        max_fields: int = MAX_UPLOAD_FIELDS
    ):
        """
        Custom form parser with increased limits for bulk uploads.
        Parser de formulario personalizado con límites aumentados para uploads masivos.
        """
        return await original_form(max_files=max_files, max_fields=max_fields)

    # Replace form method with our custom version
    self.form = custom_form  # type: ignore


def apply_multipart_patch():
    """
    Apply the multipart patch to Starlette's Request class.
    This must be called before creating the FastAPI app.

    Aplicar el parche multipart a la clase Request de Starlette.
    Esto debe llamarse antes de crear la app de FastAPI.
    """
    starlette_requests.Request.__init__ = _patched_request_init


def get_max_upload_files() -> int:
    """Get the configured maximum number of upload files."""
    return MAX_UPLOAD_FILES


def get_max_upload_fields() -> int:
    """Get the configured maximum number of upload fields."""
    return MAX_UPLOAD_FIELDS


# Apply patch on module import
# Aplicar parche al importar el módulo
apply_multipart_patch()
