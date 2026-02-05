"""
File Service / Servicio de Archivos
===================================

Service for managing uploaded files.
Servicio para gestión de archivos subidos.
"""

import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path

import aiofiles

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("uploads")


class FileService:
    """
    File management service / Servicio de gestión de archivos.

    Handles saving, retrieving, and cleaning up uploaded files.
    Maneja guardado, recuperación y limpieza de archivos subidos.

    Attributes / Atributos:
        upload_dir: Directory for uploaded files / Directorio para archivos
        _uploads: In-memory upload registry / Registro de uploads en memoria
    """

    def __init__(self, upload_dir: Path | None = None) -> None:
        """
        Initialize the file service.
        Inicializa el servicio de archivos.

        Args / Argumentos:
            upload_dir: Custom upload directory / Directorio personalizado
        """
        self.upload_dir = upload_dir or UPLOAD_DIR
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self._uploads: dict[str, dict] = {}
        logger.debug("FileService initialized with upload_dir=%s", self.upload_dir)

    async def save_upload(
        self,
        upload_id: str,
        files: list[dict],
    ) -> list[dict]:
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
            file_path = upload_path / file_data["name"]

            async with aiofiles.open(file_path, "wb") as f:
                await f.write(file_data["content"])

            saved_files.append(
                {
                    "name": file_data["name"],
                    "size": file_data["size"],
                    "type": file_data["type"],
                    "path": str(file_path),
                }
            )

            logger.debug("Saved file: %s (%d bytes)", file_data["name"], file_data["size"])

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

    async def get_upload(self, upload_id: str) -> dict | None:
        """
        Get upload information.
        Obtiene información de un upload.

        Args / Argumentos:
            upload_id: Upload identifier / Identificador del upload

        Returns / Retorna:
            Upload info dict or None / Dict de info o None
        """
        return self._uploads.get(upload_id)

    async def get_files(self, upload_id: str) -> list[dict]:
        """
        Get list of files from an upload.
        Obtiene lista de archivos de un upload.

        Args / Argumentos:
            upload_id: Upload identifier / Identificador del upload

        Returns / Retorna:
            List of file info dicts / Lista de dicts de info de archivos
        """
        upload = self._uploads.get(upload_id)
        return upload["files"] if upload else []

    async def delete_upload(self, upload_id: str) -> bool:
        """
        Delete an upload and its files.
        Elimina un upload y sus archivos.

        Args / Argumentos:
            upload_id: Upload identifier / Identificador del upload

        Returns / Retorna:
            True if deleted successfully / True si se eliminó correctamente
        """
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
        expired = [
            upload_id for upload_id, data in self._uploads.items() if data["expires_at"] < now
        ]

        for upload_id in expired:
            await self.delete_upload(upload_id)

        if expired:
            logger.info("Cleaned up %d expired uploads", len(expired))

        return len(expired)


# Global instance / Instancia global
file_service = FileService()
