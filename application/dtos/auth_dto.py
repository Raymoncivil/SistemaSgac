"""
application/dtos/auth_dto.py — Data Transfer Objects para autenticación.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LoginRequestDTO:
    """DTO para solicitud de login."""
    rut: str
    password: str


@dataclass
class LoginResponseDTO:
    """DTO para respuesta de login."""
    access_token: str
    token_type: str
    user_id: str
    rut: str
    full_name: str
    role: str


@dataclass
class LogoutRequestDTO:
    """DTO para solicitud de logout."""
    pass


@dataclass
class TokenPayloadDTO:
    """DTO para el payload del JWT token."""
    user_id: str
    rut: str
    full_name: str
    role: str
    exp: int
    iat: int
