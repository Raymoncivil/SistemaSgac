"""
presentation/api/routers/auth.py — Enrutador de autenticación.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from application.dtos.auth_dto import (
    LoginRequestDTO,
    RegisterRequestDTO
)

from application.use_cases.auth.authenticate_user import AuthenticateUserUseCase
from application.use_cases.auth.register_user import RegisterUserUseCase

from domain.exceptions import UserNotFoundError, ValidationError

from presentation.api.dependencies import (
    get_auth_service,
    get_current_user,
    get_user_repository
)

from presentation.api.schemas.auth_schema import (
    LoginRequestSchema,
    LoginResponseSchema,
    LogoutResponseSchema,
    RegisterRequestSchema,
    RegisterResponseSchema
)

router = APIRouter()


def _handle_error(exc: Exception) -> HTTPException:
    if isinstance(exc, ValidationError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    if isinstance(exc, UserNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error interno del servidor"
    )


# =========================
# LOGIN
# =========================

@router.post("/login", response_model=LoginResponseSchema)
async def login(
    payload: LoginRequestSchema,
    user_repository=Depends(get_user_repository),
    auth_service=Depends(get_auth_service),
):
    try:
        use_case = AuthenticateUserUseCase(user_repository, auth_service)
        request_dto = LoginRequestDTO(
            rut=payload.rut,
            password=payload.password
        )

        result = await use_case.execute(request_dto)

        return LoginResponseSchema(
            access_token=result.access_token,
            token_type=result.token_type,
            user_id=result.user_id,
            rut=result.rut,
            full_name=result.full_name,
            role=result.role,
        )

    except (ValidationError, UserNotFoundError) as exc:
        raise _handle_error(exc)


# =========================
# REGISTER 🔥
# =========================

@router.post("/register", response_model=RegisterResponseSchema)
async def register(
    payload: RegisterRequestSchema,
    user_repository=Depends(get_user_repository),
    auth_service=Depends(get_auth_service),
):
    try:
        use_case = RegisterUserUseCase(user_repository, auth_service)

        dto = RegisterRequestDTO(
            rut=payload.rut,
            full_name=payload.full_name,
            password=payload.password,
            role=payload.role
        )

        result = await use_case.execute(dto)

        return RegisterResponseSchema(
            user_id=result.user_id,
            rut=result.rut,
            full_name=result.full_name,
            role=result.role
        )

    except ValidationError as exc:
        raise _handle_error(exc)


# =========================
# LOGOUT
# =========================

@router.post("/logout", response_model=LogoutResponseSchema)
async def logout(_: dict = Depends(get_current_user)):
    return LogoutResponseSchema(message="Sesión cerrada correctamente")