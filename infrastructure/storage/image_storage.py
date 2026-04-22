"""
infrastructure/storage/image_storage.py — Almacenamiento de imágenes en disco.
"""

from pathlib import Path
from config import settings
from fastapi import UploadFile

UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_image_directory() -> Path:
    """Retorna el directorio de uploads."""
    return UPLOAD_DIR


async def save_image(upload_file: UploadFile, filename: str) -> str:
    """Guarda un archivo de imagen en el directorio configurado."""
    destination = UPLOAD_DIR / filename
    contents = await upload_file.read()
    destination.write_bytes(contents)
    return str(destination)


def build_image_path(filename: str) -> str:
    """Retorna la ruta de almacenamiento de una imagen."""
    return str(UPLOAD_DIR / filename)
