"""
domain/entities/activity.py — Entidad de dominio Activity.
No contiene dependencias de SQLAlchemy, FastAPI ni librerías externas.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from typing import Optional, List


@dataclass
class ChecklistItem:
    """Ítem de checklist de una actividad."""
    text: str
    done: bool = False


@dataclass
class Activity:
    """
    Entidad de dominio: Actividad del usuario en abril.
    
    Atributos:
        id: Identificador único (UUID)
        user_id: Usuario propietario
        priority_id: Prioridad (1=Alta, 2=Media, 3=Baja)
        day_of_april: Día del mes (1-30)
        title: Título de la actividad
        description: Descripción (opcional)
        emoji: Emoji representativo (opcional)
        completed: ¿Está completada?
        has_image: ¿Tiene imagen adjunta?
        image_path: Ruta de la imagen (si exists)
        checklist: Lista de ítems (checklist_items)
        created_at: Fecha de creación
        updated_at: Última actualización
    """
    
    id: UUID
    user_id: UUID
    priority_id: int
    day_of_april: int
    title: str
    description: Optional[str] = None
    emoji: Optional[str] = None
    completed: bool = False
    has_image: bool = False
    image_path: Optional[str] = None
    checklist: List[ChecklistItem] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validaciones de negocio al instanciar."""
        if not 1 <= self.day_of_april <= 30:
            raise ValueError(f"day_of_april debe estar entre 1 y 30, recibido: {self.day_of_april}")
        
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("title es requerido")
        
        if len(self.title) > 200:
            raise ValueError("title no puede exceder 200 caracteres")
        
        if self.priority_id not in (1, 2, 3):
            raise ValueError(f"priority_id debe ser 1, 2 o 3, recibido: {self.priority_id}")
        
        if self.emoji and len(self.emoji) > 10:
            raise ValueError("emoji no puede exceder 10 caracteres")
    
    def mark_completed(self):
        """Marca la actividad como completada."""
        self.completed = True
        self.updated_at = datetime.now()
    
    def mark_incomplete(self):
        """Marca la actividad como NO completada."""
        self.completed = False
        self.updated_at = datetime.now()
    
    def add_checklist_item(self, text: str):
        """Agrega un ítem al checklist."""
        if not text or len(text.strip()) == 0:
            raise ValueError("Texto del checklist no puede estar vacío")
        self.checklist.append(ChecklistItem(text=text, done=False))
        self.updated_at = datetime.now()
    
    def complete_checklist_item(self, index: int):
        """Marca un ítem del checklist como completado."""
        if 0 <= index < len(self.checklist):
            self.checklist[index].done = True
            self.updated_at = datetime.now()
    
    def get_priority_name(self) -> str:
        """Retorna el nombre de la prioridad."""
        priority_map = {1: "Alta", 2: "Media", 3: "Baja"}
        return priority_map.get(self.priority_id, "Indefinida")
