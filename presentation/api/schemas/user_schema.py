"""
presentation/api/schemas/user_schema.py — Esquemas Pydantic para usuarios.
"""

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class UserResponseSchema(BaseModel):
    id: UUID
    rut: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: datetime | None
