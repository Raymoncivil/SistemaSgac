"""
presentation/api/schemas/activity_schema.py — Esquemas Pydantic para actividades.
"""

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ChecklistItemSchema(BaseModel):
    text: str = Field(..., title="Texto del ítem")
    done: bool = Field(default=False, title="Completado")


class ActivityCreateSchema(BaseModel):
    day_of_april: int = Field(..., ge=1, le=30, title="Día de abril")
    title: str = Field(..., min_length=1, max_length=200, title="Título de la actividad")
    priority_id: int = Field(..., ge=1, le=3, title="Prioridad")
    description: Optional[str] = Field(None, title="Descripción")
    emoji: Optional[str] = Field(None, max_length=10, title="Emoji")
    checklist: Optional[List[ChecklistItemSchema]] = Field(default_factory=list)
    image_path: Optional[str] = Field(None, title="Ruta de imagen")


class ActivityUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority_id: Optional[int] = Field(None, ge=1, le=3)
    emoji: Optional[str] = Field(None, max_length=10)
    completed: Optional[bool] = None
    checklist: Optional[List[ChecklistItemSchema]] = None


class ActivityResponseSchema(BaseModel):
    id: UUID
    user_id: UUID
    day_of_april: int
    title: str
    description: Optional[str]
    emoji: Optional[str]
    priority_id: int
    priority_name: str
    completed: bool
    has_image: bool
    image_path: Optional[str]
    checklist: List[ChecklistItemSchema]
    created_at: str
    updated_at: str
