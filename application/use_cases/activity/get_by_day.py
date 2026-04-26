"""
application/use_cases/activity/get_by_day.py — Caso de uso: obtener actividades por día.
"""

from uuid import UUID
from typing import List

from domain.interfaces.activity_repository import IActivityRepository
from domain.interfaces.user_repository import IUserRepository
from domain.exceptions import UserNotFoundError
from domain.entities.activity import Activity
from ...dtos.activity_dto import ActivityResponseDTO, ChecklistItemDTO


class GetByDayUseCase:
    """Caso de uso: Obtener actividades de un usuario en un día específico."""
    
    def __init__(
        self,
        activity_repository: IActivityRepository,
        user_repository: IUserRepository
    ):
        self.activity_repo = activity_repository
        self.user_repo = user_repository
    
    async def execute(
        self,
        user_id: UUID,
        day: int
    ) -> List[ActivityResponseDTO]:
        """
        Ejecuta el caso de uso.
        
        Args:
            user_id: ID del usuario
            day: Día del mes (1-30)
        
        Returns:
            List[ActivityResponseDTO] de actividades del día
        
        Raises:
            UserNotFoundError: Si el usuario no existe
        """
        
        # 1. Validar usuario
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"Usuario {user_id} no existe")
        
        # 2. Validar day
        if not 1 <= day <= 30:
            return []
        
        # 3. Obtener actividades
        activities = await self.activity_repo.get_by_user_and_day(user_id, day)
        
        # 4. Convertir a DTOs
        return [self._to_response_dto(activity) for activity in activities]
    
    @staticmethod
    def _to_response_dto(activity: Activity) -> ActivityResponseDTO:
        """Convierte entidad a DTO."""
        return ActivityResponseDTO(
            id=str(activity.id),
            user_id=str(activity.user_id),
            day_of_april=activity.day_of_april,
            title=activity.title,
            description=activity.description or "",
            emoji=activity.emoji or "",
            priority_id=activity.priority_id,
            priority_name={1: "Baja", 2: "Media", 3: "Alta"}.get(activity.priority_id, "Sin prioridad"),
            priority_color={1: "#22C55E", 2: "#F59E0B", 3: "#EF4444"}.get(activity.priority_id, "#6B7280"),
            completed=activity.completed,
            has_image=activity.has_image,
            image_path=activity.image_path,
            checklist=[
                ChecklistItemDTO(text=item.text, done=item.done)
                for item in activity.checklist
            ],
            checklist_done=sum(1 for item in activity.checklist if item.done),
            checklist_total=len(activity.checklist),
            created_at=activity.created_at.isoformat() if activity.created_at else "",
            updated_at=activity.updated_at.isoformat() if activity.updated_at else ""
        )
