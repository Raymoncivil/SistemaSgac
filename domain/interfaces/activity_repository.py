"""
domain/interfaces/activity_repository.py — Interfaz para Activity Repository.
Define el contrato que debe cumplir cualquier implementación de persistencia.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from ..entities.activity import Activity


class IActivityRepository(ABC):
    """
    Interfaz para gerenciar persistencia de actividades.
    Las implementaciones concretas (SQLAlchemy) deben herdar de esta clase.
    Este es un ejemplo puro de Dependency Inversion Principle (DIP).
    """
    
    @abstractmethod
    async def get_by_id(self, activity_id: UUID) -> Optional[Activity]:
        """Obtiene una actividad por ID."""
        pass
    
    @abstractmethod
    async def get_by_user_and_day(self, user_id: UUID, day: int) -> List[Activity]:
        """Obtiene actividades de un usuario en un día específico."""
        pass
    
    @abstractmethod
    async def get_all_by_user(self, user_id: UUID) -> List[Activity]:
        """Obtiene todas las actividades de un usuario en abril."""
        pass
    
    @abstractmethod
    async def get_by_user_and_priority(self, user_id: UUID, priority_id: int) -> List[Activity]:
        """Obtiene actividades de un usuario filtradas por prioridad."""
        pass
    
    @abstractmethod
    async def create(self, activity: Activity) -> Activity:
        """Crea una nueva actividad."""
        pass
    
    @abstractmethod
    async def update(self, activity: Activity) -> Activity:
        """Actualiza una actividad existente."""
        pass
    
    @abstractmethod
    async def delete(self, activity_id: UUID) -> bool:
        """Elimina una actividad. Retorna True si fue exitoso."""
        pass
    
    @abstractmethod
    async def get_all_for_admin(self) -> List[Activity]:
        """Obtiene TODAS las actividades (solo admin)."""
        pass
