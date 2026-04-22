"""
domain/interfaces/user_repository.py — Interfaz para User Repository.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from ..entities.user import User


class IUserRepository(ABC):
    """
    Interfaz para gerenciar persistencia de usuarios.
    """
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Obtiene un usuario por ID."""
        pass
    
    @abstractmethod
    async def get_by_rut(self, rut: str) -> Optional[User]:
        """Obtiene un usuario por RUT."""
        pass
    
    @abstractmethod
    async def get_all_users(self) -> List[User]:
        """Obtiene todos los usuarios (solo admin)."""
        pass
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Crea un nuevo usuario."""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Actualiza un usuario existente."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Elimina un usuario."""
        pass
    
    @abstractmethod
    async def update_last_login(self, user_id: UUID) -> None:
        """Actualiza el timestamp de last_login."""
        pass
