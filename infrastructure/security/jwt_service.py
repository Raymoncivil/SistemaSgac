"""
infrastructure/security/jwt_service.py — Servicio JWT HS256 para autenticación.
"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional

from config import settings
from domain.interfaces.auth_service import IAuthService
from domain.exceptions import InvalidTokenError


class JWTService(IAuthService):
    """Servicio JWT que implementa IAuthService."""

    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = "HS256"
        self.expire_minutes = settings.access_token_expire_minutes

    def hash_password(self, plain_password: str) -> str:
        from infrastructure.security.password_hasher import hash_password as _hash_password
        return _hash_password(plain_password)

    def verify_password(self, plain_password: str, hashed: str) -> bool:
        from infrastructure.security.password_hasher import verify_password as _verify_password
        return _verify_password(plain_password, hashed)

    def create_token(self, user_id: str, rut: str, full_name: str, role: str) -> str:
        now = datetime.utcnow()
        expire = now + timedelta(minutes=self.expire_minutes)
        payload = {
            "sub": str(user_id),
            "rut": rut,
            "name": full_name,
            "role": role,
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            required_claims = {"sub", "role", "rut", "name", "iat", "exp"}
            if not required_claims.issubset(payload.keys()):
                raise InvalidTokenError("Token inválido: claims obligatorios faltantes")
            return payload
        except JWTError as exc:
            raise InvalidTokenError(f"Token inválido: {exc}")
