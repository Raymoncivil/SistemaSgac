"""
application/use_cases/activity/delete_activity.py — Caso de uso: eliminar actividad.
"""

from uuid import UUID

from domain.interfaces.activity_repository import IActivityRepository
from domain.interfaces.user_repository import IUserRepository
from domain.exceptions import ActivityNotFoundError, UnauthorizedAccessError


class DeleteActivityUseCase:
    """Caso de uso: Eliminar actividad."""
    
    def __init__(
        self,
        activity_repository: IActivityRepository,
        user_repository: IUserRepository
    ):
        self.activity_repo = activity_repository
        self.user_repo = user_repository
    
    async def execute(self, user_id: UUID, activity_id: UUID) -> bool:
        """
        Ejecuta el caso de uso.
        
        Args:
            user_id: ID del usuario que solicita
            activity_id: ID de la actividad a eliminar
        
        Returns:
            bool indicando si la eliminación fue exitosa
        
        Raises:
            ActivityNotFoundError: Si la actividad no existe
            UnauthorizedAccessError: Si el usuario no tiene permisos
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
                f"Usuario {user_id} no tiene permisos para eliminar actividad"
            )
        
        # 3. Eliminar
        success = await self.activity_repo.delete(activity_id)
        
        return success
