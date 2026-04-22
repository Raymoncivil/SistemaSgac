"""
presentation/api/routers/activities.py — Enrutador de actividades.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from ai_agent import analizar_actividad
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from application.dtos.activity_dto import ActivityCreateDTO, ActivityUpdateDTO
from application.use_cases.activity.create_activity import CreateActivityUseCase
from application.use_cases.activity.delete_activity import DeleteActivityUseCase
from application.use_cases.activity.filter_by_priority import FilterByPriorityUseCase
from application.use_cases.activity.get_all_april import GetAllAprilUseCase
from application.use_cases.activity.get_by_day import GetByDayUseCase
from application.use_cases.activity.update_activity import UpdateActivityUseCase
from domain.exceptions import (
    ActivityNotFoundError,
    UnauthorizedAccessError,
    UserNotFoundError,
    ValidationError,
)
from presentation.api.dependencies import (
    get_activity_repository,
    get_current_user,
    get_user_repository,
)
from presentation.api.schemas.activity_schema import (
    ActivityCreateSchema,
    ActivityResponseSchema,
    ActivityUpdateSchema,
)

router = APIRouter()


def _translate_error(exc: Exception) -> HTTPException:
    if isinstance(exc, ValidationError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    if isinstance(exc, UnauthorizedAccessError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(exc, (UserNotFoundError, ActivityNotFoundError)):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")


@router.get("/", response_model=list[ActivityResponseSchema])
async def list_activities(
    user_id: UUID | None = None,
    current_user: dict = Depends(get_current_user),
    activity_repo=Depends(get_activity_repository),
    user_repo=Depends(get_user_repository),
):
    try:
        target_user_id = UUID(current_user["user_id"]) if user_id is None else user_id
        use_case = GetAllAprilUseCase(activity_repo, user_repo)
        return await use_case.execute(UUID(current_user["user_id"]), target_user_id)
    except Exception as exc:
        raise _translate_error(exc)


@router.get("/day/{day}", response_model=list[ActivityResponseSchema])
async def get_activities_by_day(
    day: int,
    current_user: dict = Depends(get_current_user),
    activity_repo=Depends(get_activity_repository),
    user_repo=Depends(get_user_repository),
):
    try:
        use_case = GetByDayUseCase(activity_repo, user_repo)
        return await use_case.execute(UUID(current_user["user_id"]), day)
    except Exception as exc:
        raise _translate_error(exc)


@router.get("/priority/{priority_id}", response_model=list[ActivityResponseSchema])
async def get_activities_by_priority(
    priority_id: int,
    current_user: dict = Depends(get_current_user),
    activity_repo=Depends(get_activity_repository),
    user_repo=Depends(get_user_repository),
):
    try:
        use_case = FilterByPriorityUseCase(activity_repo, user_repo)
        return await use_case.execute(UUID(current_user["user_id"]), priority_id)
    except Exception as exc:
        raise _translate_error(exc)


@router.post("/", response_model=ActivityResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_activity(
    payload: ActivityCreateSchema,
    current_user: dict = Depends(get_current_user),
    activity_repo=Depends(get_activity_repository),
    user_repo=Depends(get_user_repository),
):
    try:
        use_case = CreateActivityUseCase(activity_repo, user_repo)

        # 🔥 IA integrada
        ia_data = analizar_actividad(payload.title)

        priority_map = {
            "alta": 1,
            "media": 2,
            "baja": 3
        }

        priority_id = priority_map.get(ia_data["prioridad"], payload.priority_id)

        request_dto = ActivityCreateDTO(
            day_of_april=payload.day_of_april,
            title=ia_data["titulo"],
            priority_id=priority_id,
            description=payload.description or ia_data["sugerencia"],
            emoji=payload.emoji,
            checklist=payload.checklist,
            image_path=payload.image_path,
        )

        return await use_case.execute(UUID(current_user["user_id"]), request_dto)

    except Exception as exc:
        raise _translate_error(exc)


@router.patch("/{activity_id}", response_model=ActivityResponseSchema)
async def update_activity(
    activity_id: UUID,
    payload: ActivityUpdateSchema,
    current_user: dict = Depends(get_current_user),
    activity_repo=Depends(get_activity_repository),
    user_repo=Depends(get_user_repository),
):
    try:
        use_case = UpdateActivityUseCase(activity_repo, user_repo)
        request_dto = ActivityUpdateDTO(
            title=payload.title,
            description=payload.description,
            priority_id=payload.priority_id,
            emoji=payload.emoji,
            completed=payload.completed,
            checklist=payload.checklist,
        )
        return await use_case.execute(UUID(current_user["user_id"]), activity_id, request_dto)
    except Exception as exc:
        raise _translate_error(exc)


@router.delete("/{activity_id}")
async def delete_activity(
    activity_id: UUID,
    current_user: dict = Depends(get_current_user),
    activity_repo=Depends(get_activity_repository),
    user_repo=Depends(get_user_repository),
):
    try:
        use_case = DeleteActivityUseCase(activity_repo, user_repo)
        success = await use_case.execute(UUID(current_user["user_id"]), activity_id)
        return {"deleted": success}
    except Exception as exc:
        raise _translate_error(exc)
        raise _translate_error(exc)
