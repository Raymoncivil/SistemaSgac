"""
presentation/api/dependencies.py — Dependencias compartidas para routers.
"""

from typing import AsyncGenerator
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.connection import get_async_session
from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.repositories.activity_repository_impl import ActivityRepositoryImpl
from infrastructure.repositories.audit_repository_impl import AuditRepositoryImpl
from infrastructure.security.jwt_service import JWTService
from domain.interfaces.user_repository import IUserRepository
from domain.interfaces.activity_repository import IActivityRepository
from domain.interfaces.audit_repository import IAuditRepository
from domain.interfaces.auth_service import IAuthService
from domain.exceptions import InvalidTokenError


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_async_session() as session:
        yield session


async def get_user_repository(db_session: AsyncSession = Depends(get_db_session)) -> IUserRepository:
    return UserRepositoryImpl(db_session)


async def get_activity_repository(db_session: AsyncSession = Depends(get_db_session)) -> IActivityRepository:
    return ActivityRepositoryImpl(db_session)


async def get_audit_repository(db_session: AsyncSession = Depends(get_db_session)) -> IAuditRepository:
    return AuditRepositoryImpl(db_session)


async def get_auth_service() -> IAuthService:
    return JWTService()


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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )

    return {
        "user_id": payload["sub"],
        "rut": payload.get("rut"),
        "full_name": payload.get("name"),
        "role": payload.get("role"),
    }


def require_roles(*allowed_roles: str):
    async def role_dependency(current_user: dict = Depends(get_current_user)) -> dict:
        current_role = (current_user.get("role") or "").lower()
        if current_role not in {role.lower() for role in allowed_roles}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para acceder a este recurso",
            )
        return current_user

    return role_dependency


async def get_current_admin(current_user: dict = Depends(require_roles("admin"))) -> dict:
    return current_user
