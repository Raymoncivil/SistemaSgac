"""
application/use_cases/activity/get_all_april.py — Caso de uso: obtener todas las actividades de abril.
"""

from uuid import UUID
from typing import List

from domain.interfaces.activity_repository import IActivityRepository
from domain.interfaces.user_repository import IUserRepository
from domain.exceptions import UserNotFoundError, UnauthorizedAccessError
from domain.entities.activity import Activity
from ...dtos.activity_dto import ActivityResponseDTO, ChecklistItemDTO


class GetAllAprilUseCase:
    """Caso de uso: Obtener todas las actividades de un usuario en abril."""
    
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
        target_user_id: UUID = None
    ) -> List[ActivityResponseDTO]:
        """
        Ejecuta el caso de uso.
        
        Args:
            user_id: ID del usuario que solicita
            target_user_id: ID del usuario cuyas actividades se solicitan
                            Si None, se asume target_user_id = user_id
        
        Returns:
            List[ActivityResponseDTO] de todas las actividades
        
        Raises:
            UserNotFoundError: Si algún usuario no existe
            UnauthorizedAccessError: Si el usuario no tiene permisos
        """
        
        # 1. Si no se especifica target_user_id, asumir el usuario mismo
        if target_user_id is None:
            target_user_id = user_id
        
        # 2. Validar usuarios
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"Usuario {user_id} no existe")
        
        target_user = await self.user_repo.get_by_id(target_user_id)
        if not target_user:
            raise UserNotFoundError(f"Usuario objetivo {target_user_id} no existe")
        
        # 3. Validar autorización
        # Un usuario solo puede ver sus propias actividades, salvo que sea admin
        if user_id != target_user_id and user.role != 'admin':
            raise UnauthorizedAccessError(
                f"Usuario {user_id} no tiene permisos para ver actividades de {target_user_id}"
            )
        
        # 4. Obtener actividades
        activities = await self.activity_repo.get_all_by_user(target_user_id)
        
        # 5. Convertir a DTOs
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
