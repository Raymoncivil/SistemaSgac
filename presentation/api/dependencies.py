"""
presentation/api/dependencies.py — Dependencias de FastAPI.
"""

from fastapi import Depends, HTTPException, status, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from domain.interfaces.auth_service import IAuthService
from domain.exceptions import InvalidTokenError

from infrastructure.security.jwt_service import JWTService

# ⚠️ AJUSTA ESTA IMPORTACIÓN SEGÚN TU PROYECTO

from infrastructure.database.database import get_db_session
from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.repositories.activity_repository_impl import ActivityRepositoryImpl

from infrastructure.repositories.audit_repository_impl import AuditRepositoryImpl

async def get_audit_repository(
    db: AsyncSession = Depends(get_db_session)
):
    return AuditRepositoryImpl(db)

# =========================
# AUTH SERVICE
# =========================

def get_auth_service() -> IAuthService:
    return JWTService()


# =========================
# DB SESSION
# =========================

async def get_db(db: AsyncSession = Depends(get_db_session)):
    return db


# =========================
# REPOSITORIES
# =========================

def get_user_repository(
    db: AsyncSession = Depends(get_db_session),
):
    return UserRepositoryImpl(db)

async def get_activity_repository(
    db: AsyncSession = Depends(get_db_session)
):
    return ActivityRepositoryImpl(db)


# =========================
# CURRENT USER (JWT)
# =========================

async def get_current_user(
    request: Request,
    authorization: str | None = Header(default=None),
    auth_service: IAuthService = Depends(get_auth_service),
) -> dict:

    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere token Bearer en Authorization header",
        )

    token = authorization.removeprefix("Bearer ").strip()

    try:
        payload = auth_service.verify_token(token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc)
        )

    required_fields = {"sub", "role", "rut", "name"}

    if not payload or not required_fields.issubset(payload.keys()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o incompleto",
        )

    return {
        "user_id": payload["sub"],
        "rut": payload.get("rut"),
        "full_name": payload.get("name"),
        "role": payload.get("role"),
    }


# =========================
# ROLES (RBAC)
# =========================

def require_roles(*allowed_roles: str):

    async def role_dependency(
        current_user: dict = Depends(get_current_user)
    ) -> dict:

        current_role = (current_user.get("role") or "").lower()
        allowed = [role.lower() for role in allowed_roles]

        if current_role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para acceder a este recurso",
            )

        return current_user

    return role_dependency


async def get_current_admin(
    current_user: dict = Depends(require_roles("admin"))
) -> dict:
    return current_user
