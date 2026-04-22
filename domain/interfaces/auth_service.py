"""
domain/interfaces/auth_service.py — Interfaz para Auth Service.
Define el contrato de autenticación (JWT, contraseñas, etc).
"""

from abc import ABC, abstractmethod
from typing import Optional


class IAuthService(ABC):
    """
    Interfaz para servicios de autenticación.
    Las implementaciones concretas (JWT, OAuth, etc) deben heredar de esta.
    """
    
    @abstractmethod
    def hash_password(self, plain_password: str) -> str:
        """Hashea una contraseña en texto plano."""
        pass
    
    @abstractmethod
    def verify_password(self, plain_password: str, hashed: str) -> bool:
        """Verifica si una contraseña coincide con su hash."""
        pass
    
    @abstractmethod
    def create_token(self, user_id: str, rut: str, full_name: str, role: str) -> str:
        """Crea un JWT token."""
        pass
    
    @abstractmethod
    def verify_token(self, token: str) -> Optional[dict]:
        """
        Verifica y decodifica un JWT token.
        
        Retorna:
            dict con {user_id, rut, full_name, role, exp} o None si token inválido
        """
        pass
