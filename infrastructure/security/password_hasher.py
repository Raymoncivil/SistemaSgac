"""
infrastructure/security/password_hasher.py — Hashing de contraseñas con bcrypt.
"""

import bcrypt


def hash_password(plain_password: str) -> str:
    """Hashea la contraseña en texto plano usando bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except ValueError:
        return False
