"""
domain/interfaces/audit_repository.py — Interfaz para Audit Repository.
"""

from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from ..entities.audit_log import AuditLog


class IAuditRepository(ABC):
    """
    Interfaz para gerenciar logs de auditoría.
    """
    
    @abstractmethod
    async def create(self, audit_log: AuditLog) -> AuditLog:
        """Registra una acción en auditoría."""
        pass
    
    @abstractmethod
    async def get_all_logs(self) -> List[AuditLog]:
        """Obtiene todos los logs (solo admin)."""
        pass
    
    @abstractmethod
    async def get_logs_by_user(self, user_id: UUID) -> List[AuditLog]:
        """Obtiene logs de un usuario específico."""
        pass
    
    @abstractmethod
    async def get_logs_by_entity(self, entity_id: UUID) -> List[AuditLog]:
        """Obtiene logs de una entidad específica."""
        pass
