"""
application/use_cases/activity/create_activity.py — Caso de uso: crear actividad.
Orquesta la lógica de negocio para crear una nueva actividad.
"""

from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional, List

from domain.entities.activity import Activity, ChecklistItem
from domain.interfaces.activity_repository import IActivityRepository
from domain.interfaces.user_repository import IUserRepository
from domain.exceptions import (
    UserNotFoundError,
    ValidationError,
    UnauthorizedAccessError
)
from ...dtos.activity_dto import ActivityCreateDTO, ActivityResponseDTO, ChecklistItemDTO


class CreateActivityUseCase:
    """
    Caso de uso: Crear actividad.
    
    Responsabilidades:
    - Validar datos de entrada
    - Verificar que el usuario exista
    - Crear entidad Activity con reglas de negocio
    - Persistir mediante el repositorio
    - Retornar DTO de respuesta
    """
    
    def __init__(
        self,
        activity_repository: IActivityRepository,
        user_repository: IUserRepository
    ):
        """
        Inyección de dependencias.
        
        Args:
            activity_repository: Implementación de IActivityRepository
            user_repository: Implementación de IUserRepository
        """
        self.activity_repo = activity_repository
        self.user_repo = user_repository
    
    async def execute(
        self,
        user_id: UUID,
        activity_dto: ActivityCreateDTO
    ) -> ActivityResponseDTO:
        """
        Ejecuta el caso de uso.
        
        Args:
            user_id: ID del usuario propietario de la actividad
            activity_dto: DTO con datos de la actividad
        
        Returns:
            ActivityResponseDTO con la actividad creada
        
        Raises:
            UserNotFoundError: Si el usuario no existe
            ValidationError: Si los datos son inválidos
        """
        
        # 1. Validar que el usuario existe
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"Usuario con ID {user_id} no existe")
        
        # 2. Crear entidad de dominio (las validaciones ocurren en __post_init__)
        try:
            activity = Activity(
                id=uuid4(),
                user_id=user_id,
                priority_id=activity_dto.priority_id,
                day_of_april=activity_dto.day_of_april,
                title=activity_dto.title,
                description=activity_dto.description,
                emoji=activity_dto.emoji,
                completed=False,
                has_image=bool(activity_dto.image_path),
                image_path=activity_dto.image_path,
                checklist=[
                    ChecklistItem(text=item.text, done=item.done)
                    for item in activity_dto.checklist
                ],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
        except ValueError as e:
            raise ValidationError(str(e))
        
        # 3. Persistir
        saved_activity = await self.activity_repo.create(activity)
        
        # 4. Retornar DTO de respuesta
        return self._to_response_dto(saved_activity)
    
    @staticmethod
    def _to_response_dto(activity: Activity) -> ActivityResponseDTO:
        """Convierte entidad Activity a DTO para respuesta."""
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
