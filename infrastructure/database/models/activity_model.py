"""
infrastructure/database/models/activity_model.py — Modelo ORM de actividades.
"""

from sqlalchemy import Column, String, Text, Boolean, SmallInteger, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from . import Base
import uuid


class ActivityModel(Base):
    __tablename__ = "activities"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    priority_id = Column(Integer, nullable=False)
    day_of_april = Column(SmallInteger, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    emoji = Column(String(10), nullable=True)
    completed = Column(Boolean, nullable=False, default=False)
    has_image = Column(Boolean, nullable=False, default=False)
    image_path = Column(String(500), nullable=True)
    checklist_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    # relationship eliminado — user_id FK es suficiente para las queriesc