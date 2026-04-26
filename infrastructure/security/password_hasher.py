"""
infrastructure/security/password_hasher.py
Servicio de hashing de contraseñas usando bcrypt.
"""

import bcrypt


def hash_password(plain_password: str) -> str:
    """
    Genera un hash seguro de una contraseña en texto plano.

    Args:
        plain_password (str): Contraseña sin encriptar

    Returns:
        str: Contraseña hasheada (bcrypt)
    """
    if not plain_password or len(plain_password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")

    salt = bcrypt.gensalt(rounds=12)  # 🔥 nivel seguro recomendado
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)

    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.

    Args:
        plain_password (str): Contraseña ingresada
        hashed_password (str): Hash almacenado en BD

    Returns:
        bool: True si coincide, False si no
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False
