"""
application/dtos/activity_dto.py — Data Transfer Objects para Activity.
Estos DTOs viajan entre capas, no son entidades de dominio.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from uuid import UUID


@dataclass
class ChecklistItemDTO:
    """DTO para un ítem del checklist."""
    text: str
    done: bool = False


@dataclass
class ActivityCreateDTO:
    """DTO para crear una actividad (input del cliente)."""
    day_of_april: int
    title: str
    priority_id: int
    description: Optional[str] = None
    emoji: Optional[str] = None
    checklist: List[ChecklistItemDTO] = field(default_factory=list)
    image_path: Optional[str] = None


@dataclass
class ActivityUpdateDTO:
    """DTO para actualizar una actividad (PATCH)."""
    title: Optional[str] = None
    description: Optional[str] = None
    priority_id: Optional[int] = None
    emoji: Optional[str] = None
    completed: Optional[bool] = None
    checklist: Optional[List[ChecklistItemDTO]] = None


@dataclass
class ActivityResponseDTO:
    """DTO para responder una actividad (output al cliente)."""
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
    checklist: List[ChecklistItemDTO]
    created_at: str  # ISO format
    updated_at: str  # ISO format
