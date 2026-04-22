"""
domain/entities/user.py — Entidad de dominio User.
No contiene dependencias de SQLAlchemy, FastAPI ni librerías externas.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Optional


@dataclass
class User:
    """
    Entidad de dominio: Usuario del sistema.
    
    Atributos:
        id: Identificador único (UUID)
        rut: RUT chileno sin formato (ej: 123456789)
        full_name: Nombre completo del usuario
        password_hash: Hash bcrypt de la contraseña (nunca la contraseña plana)
        role: 'user' o 'admin'
        is_active: Si el usuario está activo
        created_at: Fecha de creación
        last_login: Último login
    """
    
    id: UUID
    rut: str
    full_name: str
    password_hash: str
    role: str  # 'user' o 'admin'
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    def __post_init__(self):
        """Validaciones de negocio ejecutadas al instanciar."""
        if self.role not in ('user', 'admin'):
            raise ValueError(f"Role debe ser 'user' o 'admin', recibido: {self.role}")
        
        if not self.rut or len(self.rut) < 8:
            raise ValueError("RUT debe tener al menos 8 caracteres")
    
    def is_admin(self) -> bool:
        """¿Es administrador?"""
        return self.role == 'admin'
    
    def is_user(self) -> bool:
        """¿Es usuario regular?"""
        return self.role == 'user'
    
    def can_manage_activity(self, activity_user_id: UUID) -> bool:
        """
        ¿Puede este usuario gestionar una actividad?
        
        Reglas:
        - admin puede gestionar cualquier actividad
        - user solo puede gestionar sus propias actividades
        """
        if self.is_admin():
            return True
        return self.id == activity_user_id
