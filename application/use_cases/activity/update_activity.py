"""
application/use_cases/activity/update_activity.py — Caso de uso: actualizar actividad (PATCH).
"""

from uuid import UUID
from datetime import datetime
from typing import Optional

from domain.entities.activity import Activity, ChecklistItem
from domain.interfaces.activity_repository import IActivityRepository
from domain.interfaces.user_repository import IUserRepository
from domain.exceptions import ActivityNotFoundError, UnauthorizedAccessError, ValidationError
from ...dtos.activity_dto import ActivityUpdateDTO, ActivityResponseDTO, ChecklistItemDTO


class UpdateActivityUseCase:
    """
    Caso de uso: Actualizar actividad (PATCH).
    
    Solo actualiza los campos que vienen en el DTO (null = no cambiar).
    """
    
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
        activity_id: UUID,
        update_dto: ActivityUpdateDTO
    ) -> ActivityResponseDTO:
        """
        Ejecuta el caso de uso.
        
        Args:
            user_id: ID del usuario que solicita (validación de propiedad)
            activity_id: ID de la actividad a actualizar
            update_dto: DTO con campos a actualizar
        
        Returns:
            ActivityResponseDTO actualizada
        
        Raises:
            ActivityNotFoundError: Si la actividad no existe
            UnauthorizedAccessError: Si el usuario no es propietario y no es admin
            ValidationError: Si los datos son inválidos
        """
        
        # 1. Obtener actividad
        activity = await self.activity_repo.get_by_id(activity_id)
        if not activity:
            raise ActivityNotFoundError(f"Actividad {activity_id} no existe")
        
        # 2. Validar autorización
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ActivityNotFoundError(f"Usuario {user_id} no existe")
        
        if not user.can_manage_activity(activity.user_id):
            raise UnauthorizedAccessError(
                f"Usuario {user_id} no tiene permisos para modificar actividad de {activity.user_id}"
            )
        
        # 3. Aplicar cambios (solo los campos que vienen en el DTO)
        try:
            if update_dto.title is not None:
                activity.title = update_dto.title
            
            if update_dto.description is not None:
                activity.description = update_dto.description
            
            if update_dto.priority_id is not None:
                if update_dto.priority_id not in (1, 2, 3):
                    raise ValidationError("priority_id debe ser 1, 2 o 3")
                activity.priority_id = update_dto.priority_id
            
            if update_dto.emoji is not None:
                activity.emoji = update_dto.emoji
            
            if update_dto.completed is not None:
                if update_dto.completed:
                    activity.mark_completed()
                else:
                    activity.mark_incomplete()
            
            if update_dto.checklist is not None:
                activity.checklist = [
                    ChecklistItem(text=item.text, done=item.done)
                    for item in update_dto.checklist
                ]
            
            activity.updated_at = datetime.now()
        
        except ValueError as e:
            raise ValidationError(str(e))
        
        # 4. Persistir
        saved_activity = await self.activity_repo.update(activity)
        
        # 5. Retornar DTO
        return self._to_response_dto(saved_activity)
    
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
