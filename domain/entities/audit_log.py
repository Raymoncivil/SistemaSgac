"""
domain/entities/audit_log.py — Entidad de dominio AuditLog.
Registra todas las operaciones de modificación/eliminación.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Optional


@dataclass
class AuditLog:
    """
    Entidad de dominio: Log de auditoría.
    
    Atributos:
        id: Identificador único
        user_id: Usuario que realizó la acción (puede ser None si fue eliminado)
        action: Acción realizada (CREATE_ACTIVITY, UPDATE_ACTIVITY, DELETE_ACTIVITY)
        entity_type: Tipo de entidad afectada (Activity, User)
        entity_id: ID de la entidad afectada
        old_value: Valor anterior (para PATCH/DELETE)
        new_value: Valor nuevo (para CREATE/PATCH)
        ip_address: IP del cliente
        created_at: Timestamp de la acción
    """
    
    id: UUID
    action: str
    entity_type: str
    entity_id: UUID
    ip_address: str
    created_at: datetime
    user_id: Optional[UUID] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    
    def __post_init__(self):
        """Validaciones de negocio."""
        valid_actions = {
            'CREATE_ACTIVITY', 'UPDATE_ACTIVITY', 'DELETE_ACTIVITY',
            'CREATE_USER', 'UPDATE_USER', 'DELETE_USER',
            'LOGIN', 'LOGOUT'
        }
        if self.action not in valid_actions:
            raise ValueError(f"Action debe ser uno de {valid_actions}, recibido: {self.action}")
        
        valid_entity_types = {'Activity', 'User', 'Session'}
        if self.entity_type not in valid_entity_types:
            raise ValueError(f"entity_type debe ser uno de {valid_entity_types}, recibido: {self.entity_type}")
