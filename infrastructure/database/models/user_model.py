"""
infrastructure/database/models/user_model.py — Modelo ORM de usuarios.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from . import Base
import enum
import uuid


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class UserModel(Base):
    __tablename__ = "users"

    # UUID nativo para PostgreSQL
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    rut = Column(String(20), unique=True, nullable=False)
    full_name = Column(String(150), nullable=False)
    password_hash = Column(String(255), nullable=False)

    role = Column(Enum(UserRole), nullable=False, default=UserRole.user)
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
