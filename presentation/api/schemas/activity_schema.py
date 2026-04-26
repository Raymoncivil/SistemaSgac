"""
presentation/api/schemas/activity_schema.py — Esquemas Pydantic para actividades.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ChecklistItemSchema(BaseModel):
    text: str = Field(..., title="Texto del ítem")
    done: bool = Field(default=False, title="Completado")

    model_config = {"from_attributes": True}


class ActivityCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    day: int = Field(..., ge=1, le=30)
    priority_id: int = Field(..., ge=1, le=3)
    description: str = ""
    emoji: str = Field("", max_length=10)
    checklist: List[ChecklistItemSchema] = Field(default_factory=list)


class ActivityUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    priority_id: Optional[int] = Field(None, ge=1, le=3)
    description: Optional[str] = None
    emoji: Optional[str] = Field(None, max_length=10)
    completed: Optional[bool] = None
    checklist: Optional[List[ChecklistItemSchema]] = None


class ActivityResponse(BaseModel):
    id: str
    title: str
    day_of_april: int
    priority_id: int
    priority_name: str
    priority_color: str
    description: str
    emoji: str
    completed: bool
    has_image: bool
    image_path: Optional[str] = None
    checklist: List[ChecklistItemSchema] = []
    checklist_done: int
    checklist_total: int
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}