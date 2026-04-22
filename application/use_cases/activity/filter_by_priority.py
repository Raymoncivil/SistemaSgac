"""
application/use_cases/activity/filter_by_priority.py — Caso de uso: filtrar actividades por prioridad.
"""

from uuid import UUID
from typing import List

from domain.interfaces.activity_repository import IActivityRepository
from domain.interfaces.user_repository import IUserRepository
from domain.exceptions import UserNotFoundError, ValidationError
from domain.entities.activity import Activity
from ...dtos.activity_dto import ActivityResponseDTO, ChecklistItemDTO


class FilterByPriorityUseCase:
    """Caso de uso: Filtrar actividades de un usuario por prioridad."""
    
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
        priority_id: int
    ) -> List[ActivityResponseDTO]:
        """
        Ejecuta el caso de uso.
        
        Args:
            user_id: ID del usuario
            priority_id: ID de prioridad (1=Alta, 2=Media, 3=Baja)
        
        Returns:
            List[ActivityResponseDTO] filtradas por prioridad
        
        Raises:
            UserNotFoundError: Si el usuario no existe
            ValidationError: Si la prioridad es inválida
        """
        
        # 1. Validar usuario
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"Usuario {user_id} no existe")
        
        # 2. Validar prioridad
        if priority_id not in (1, 2, 3):
            raise ValidationError("priority_id debe ser 1, 2 o 3")
        
        # 3. Obtener actividades filtradas
        activities = await self.activity_repo.get_by_user_and_priority(
            user_id,
            priority_id
        )
        
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
