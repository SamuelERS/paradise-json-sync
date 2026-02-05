"""
File Service / Servicio de Archivos
===================================

Service for managing uploaded files.
Servicio para gestión de archivos subidos.
"""

import asyncio
import logging
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import aiofiles

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("uploads")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal attacks.
    Sanitiza un nombre de archivo para prevenir ataques de path traversal.

    Args / Argumentos:
        filename: Original filename / Nombre de archivo original

    Returns / Retorna:
        Safe filename with only the base name / Nombre seguro solo con el nombre base
    """
    # Extract only the base filename, removing any path components
    # Extraer solo el nombre base, removiendo cualquier componente de path
    safe_name = Path(filename).name

    # Remove any remaining dangerous characters
    # Remover cualquier caracter peligroso restante
    safe_name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', safe_name)

    # Ensure the filename is not empty
    if not safe_name or safe_name in ('.', '..'):
        safe_name = 'unnamed_file'

    return safe_name


class FileService:
    """
    File management service / Servicio de gestión de archivos.

    Handles saving, retrieving, and cleaning up uploaded files.
    Maneja guardado, recuperación y limpieza de archivos subidos.

    Attributes / Atributos:
        upload_dir: Directory for uploaded files / Directorio para archivos
        _uploads: In-memory upload registry / Registro de uploads en memoria
    """

    def __init__(self, upload_dir: Optional[Path] = None) -> None:
        """
        Initialize the file service.
        Inicializa el servicio de archivos.

        Args / Argumentos:
            upload_dir: Custom upload directory / Directorio personalizado
        """
        self.upload_dir = upload_dir or UPLOAD_DIR
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self._uploads: Dict[str, dict] = {}
        # Lock for thread-safe access to _uploads dict
        # Lock para acceso thread-safe al dict _uploads
        self._lock = asyncio.Lock()
        logger.debug("FileService initialized with upload_dir=%s", self.upload_dir)

    async def save_upload(
        self,
        upload_id: str,
        files: List[dict],
    ) -> List[dict]:
        """
        Save uploaded files to disk.
        Guarda archivos subidos en disco.

        Args / Argumentos:
            upload_id: Unique upload identifier / Identificador único
            files: List of file data dicts / Lista de datos de archivos

        Returns / Retorna:
            List of saved file info / Lista de info de archivos guardados
        """
        upload_path = self.upload_dir / upload_id
        upload_path.mkdir(parents=True, exist_ok=True)

        saved_files = []
        for file_data in files:
            # SECURITY: Sanitize filename to prevent path traversal
            # SEGURIDAD: Sanitizar nombre de archivo para prevenir path traversal
            safe_name = sanitize_filename(file_data["name"])
            file_path = upload_path / safe_name

            async with aiofiles.open(file_path, "wb") as f:
                await f.write(file_data["content"])

            saved_files.append(
                {
                    "name": safe_name,
                    "original_name": file_data["name"],
                    "size": file_data["size"],
                    "type": file_data["type"],
                    "path": str(file_path),
                }
            )

            logger.debug("Saved file: %s (%d bytes)", safe_name, file_data["size"])

        # Thread-safe update of uploads registry
        # Actualización thread-safe del registro de uploads
        async with self._lock:
            self._uploads[upload_id] = {
                "files": saved_files,
                "total_files": len(saved_files),
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=24),
            }

        logger.info(
            "Upload %s saved with %d files",
            upload_id,
            len(saved_files),
        )

        return saved_files

    async def get_upload(self, upload_id: str) -> Optional[dict]:
        """
        Get upload information.
        Obtiene información de un upload.

        Args / Argumentos:
            upload_id: Upload identifier / Identificador del upload

        Returns / Retorna:
            Upload info dict or None / Dict de info o None
        """
        async with self._lock:
            return self._uploads.get(upload_id)

    async def get_files(self, upload_id: str) -> List[dict]:
        """
        Get list of files from an upload.
        Obtiene lista de archivos de un upload.

        Args / Argumentos:
            upload_id: Upload identifier / Identificador del upload

        Returns / Retorna:
            List of file info dicts / Lista de dicts de info de archivos
        """
        async with self._lock:
            upload = self._uploads.get(upload_id)
            return upload.get("files", []) if upload else []

    async def delete_upload(self, upload_id: str) -> bool:
        """
        Delete an upload and its files.
        Elimina un upload y sus archivos.

        Args / Argumentos:
            upload_id: Upload identifier / Identificador del upload

        Returns / Retorna:
            True if deleted successfully / True si se eliminó correctamente
        """
        async with self._lock:
            if upload_id not in self._uploads:
                return False

            upload_path = self.upload_dir / upload_id
            if upload_path.exists():
                shutil.rmtree(upload_path)

            del self._uploads[upload_id]

        logger.info("Deleted upload: %s", upload_id)
        return True

    async def cleanup_expired(self) -> int:
        """
        Clean up expired uploads.
        Limpia uploads expirados.

        Returns / Retorna:
            Number of uploads cleaned up / Número de uploads limpiados
        """
        now = datetime.utcnow()

        # Get expired upload IDs under lock
        async with self._lock:
            expired = [
                upload_id for upload_id, data in self._uploads.items()
                if data.get("expires_at", now) < now
            ]

        # Delete each expired upload (delete_upload has its own lock)
        deleted_count = 0
        for upload_id in expired:
            if await self.delete_upload(upload_id):
                deleted_count += 1

        if deleted_count:
            logger.info("Cleaned up %d expired uploads", deleted_count)

        return deleted_count


# Global instance / Instancia global
file_service = FileService()
