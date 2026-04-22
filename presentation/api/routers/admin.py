"""
presentation/api/routers/admin.py — Enrutador de administración (solo admin).
"""

from fastapi import APIRouter, Depends, HTTPException, status

from domain.exceptions import ValidationError
from presentation.api.dependencies import (
    get_audit_repository,
    get_current_admin,
    get_user_repository,
)
from presentation.api.schemas.admin_schema import (
    AdminUserResponseSchema,
    AuditLogResponseSchema,
)

router = APIRouter()


def _handle_admin_error(exc: Exception) -> HTTPException:
    if isinstance(exc, ValidationError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")


@router.get("/users", response_model=list[AdminUserResponseSchema])
async def list_users_admin(
    _: dict = Depends(get_current_admin),
    user_repo=Depends(get_user_repository),
):
    try:
        users = await user_repo.get_all_users()
        return [
            AdminUserResponseSchema(
                id=user.id,
                rut=user.rut,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
                last_login=user.last_login,
            )
            for user in users
        ]
    except Exception as exc:
        raise _handle_admin_error(exc)


@router.get("/audit-logs", response_model=list[AuditLogResponseSchema])
async def list_audit_logs_admin(
    _: dict = Depends(get_current_admin),
    audit_repo=Depends(get_audit_repository),
):
    try:
        logs = await audit_repo.get_all_logs()
        return [
            AuditLogResponseSchema(
                id=log.id,
                user_id=log.user_id,
                action=log.action,
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                old_value=log.old_value,
                new_value=log.new_value,
                ip_address=log.ip_address,
                created_at=log.created_at,
            )
            for log in logs
        ]
    except Exception as exc:
        raise _handle_admin_error(exc)
