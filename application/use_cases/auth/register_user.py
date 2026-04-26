from domain.interfaces.user_repository import IUserRepository
from domain.interfaces.auth_service import IAuthService
from domain.value_objects.rut import RUT
from domain.exceptions import ValidationError
from application.dtos.auth_dto import RegisterRequestDTO, RegisterResponseDTO


class RegisterUserUseCase:

    def __init__(self, user_repository: IUserRepository, auth_service: IAuthService):
        self.user_repo = user_repository
        self.auth_service = auth_service

    async def execute(self, dto: RegisterRequestDTO) -> RegisterResponseDTO:

        if not RUT.validate(dto.rut):
            raise ValidationError("RUT inválido")

        rut_clean = RUT.clean_format(dto.rut)

        existing = await self.user_repo.get_by_rut(rut_clean)
        if existing:
            raise ValidationError("El usuario ya existe")

        if len(dto.password) < 8:
            raise ValidationError("La contraseña debe tener mínimo 8 caracteres")

        hashed_password = self.auth_service.hash_password(dto.password)

        user = await self.user_repo.create_user(
            rut=rut_clean,
            full_name=dto.full_name,
            password_hash=hashed_password,
            role=dto.role
        )

        return RegisterResponseDTO(
            user_id=str(user.id),
            rut=user.rut,
            full_name=user.full_name,
            role=user.role
        )