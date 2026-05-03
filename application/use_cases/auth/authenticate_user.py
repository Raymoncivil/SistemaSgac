"""
application/use_cases/auth/authenticate_user.py — Caso de uso: autenticar usuario.
"""

from uuid import UUID

from domain.interfaces.user_repository import IUserRepository
from domain.interfaces.auth_service import IAuthService
from domain.value_objects.rut import RUT
from domain.exceptions import (
    InvalidRUTFormatException,
    InvalidRUTDVException,
    UserNotFoundError,
    UserInactiveException,
    WrongPasswordException,
    ValidationError
)
from ...dtos.auth_dto import LoginRequestDTO, LoginResponseDTO, TokenPayloadDTO


class AuthenticateUserUseCase:
    """
    Caso de uso: Autenticar usuario (login).
    
    Responsabilidades:
    - Validar RUT chileno
    - Verificar que el usuario existe en BD
    - Validar contraseña
    - Generar JWT token
    - Actualizar last_login
    """
    
    def __init__(
        self,
        user_repository: IUserRepository,
        auth_service: IAuthService
    ):
        self.user_repo = user_repository
        self.auth_service = auth_service
    
    async def execute(self, login_dto: LoginRequestDTO) -> LoginResponseDTO:
        """
        Ejecuta el caso de uso.
        
        Args:
            login_dto: DTO con RUT y contraseña
        
        Returns:
            LoginResponseDTO con token y datos del usuario
        
        Raises:
            InvalidRUTException: Si el RUT es inválido
            UserNotFoundError: Si el usuario no existe
            ValidationError: Si la contraseña es incorrecta
        """
        
        # 1. Validar RUT (módulo 11) - Lanza InvalidRUTFormatException o InvalidRUTDVException directamente
        RUT.validate(login_dto.rut)
        
        # 2. Limpiar RUT
        rut_clean = RUT.clean_format(login_dto.rut)
        
        # 3. Obtener usuario por RUT
        user = await self.user_repo.get_by_rut(rut_clean)
        if not user:
            raise UserNotFoundError(f"Usuario con RUT {rut_clean} no existe")
        
        # 4. Verificar que el usuario está activo
        if not user.is_active:
            raise UserInactiveException("Usuario inactivo")
        
        # 5. Validar contraseña
        if not self.auth_service.verify_password(login_dto.password, user.password_hash):
            raise WrongPasswordException("Contraseña incorrecta")
        
        # 6. Generar token JWT
        token = self.auth_service.create_token(
            user_id=str(user.id),
            rut=user.rut,
            full_name=user.full_name,
            role=user.role
        )
        
        # 7. Actualizar last_login
        await self.user_repo.update_last_login(user.id)
        
        # 8. Retornar DTO de respuesta
        return LoginResponseDTO(
            access_token=token,
            token_type="bearer",
            user_id=str(user.id),
            rut=user.rut,
            full_name=user.full_name,
            role=user.role
        )
