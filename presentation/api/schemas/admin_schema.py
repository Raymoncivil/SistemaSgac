"""
presentation/api/schemas/admin_schema.py — Esquemas Pydantic para endpoints admin.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AdminUserResponseSchema(BaseModel):
    id: UUID | str
    rut: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: datetime | None = None


class AuditLogResponseSchema(BaseModel):
    id: UUID
    user_id: UUID | None = None
    action: str
    entity_type: str
    entity_id: UUID
    old_value: str | None = None
    new_value: str | None = None
    ip_address: str
    created_at: datetime
