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
            id=activity.id,
            user_id=activity.user_id,
            day_of_april=activity.day_of_april,
            title=activity.title,
            description=activity.description,
            emoji=activity.emoji,
            priority_id=activity.priority_id,
            priority_name=activity.get_priority_name(),
            completed=activity.completed,
            has_image=activity.has_image,
            image_path=activity.image_path,
            checklist=[
                ChecklistItemDTO(text=item.text, done=item.done)
                for item in activity.checklist
            ],
            created_at=activity.created_at.isoformat(),
            updated_at=activity.updated_at.isoformat()
        )
