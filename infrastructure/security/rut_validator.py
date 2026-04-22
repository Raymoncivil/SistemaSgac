"""
infrastructure/security/rut_validator.py — Validador de RUT chileno.
"""

from domain.value_objects.rut import RUT
from domain.exceptions import InvalidRUTException


def validate_rut(rut: str) -> bool:
    """Valida el RUT chileno y retorna True si es correcto."""
    try:
        return RUT.validate(rut)
    except InvalidRUTException:
        return False


def normalize_rut(rut: str) -> str:
    """Retorna el RUT limpiado y normalizado."""
    return RUT.clean_format(rut)
