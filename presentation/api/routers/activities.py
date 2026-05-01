"""
presentation/api/routers/activities.py — Enrutador de actividades.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Path, Response
from sqlalchemy.ext.asyncio import AsyncSession
from application.dtos.activity_dto import ActivityCreateDTO, ActivityUpdateDTO
from application.use_cases.activity.create_activity import CreateActivityUseCase
from application.use_cases.activity.delete_activity import DeleteActivityUseCase
from application.use_cases.activity.filter_by_priority import FilterByPriorityUseCase
from application.use_cases.activity.get_all_april import GetAllAprilUseCase
from application.use_cases.activity.get_by_day import GetByDayUseCase
from application.use_cases.activity.update_activity import UpdateActivityUseCase
from domain.exceptions import (
    ActivityNotFoundError, UnauthorizedAccessError,
    UserNotFoundError, ValidationError,
)
from presentation.api.dependencies import (
    get_activity_repository, get_current_user, get_user_repository, get_db_session,
)
from presentation.api.schemas.activity_schema import (
    ActivityCreateRequest, ActivityResponse, ActivityUpdateRequest,
)
import json as _json
import uuid as _uuid
from datetime import datetime, timezone
import traceback as tb 
from infrastructure.database.models.activity_model import ActivityModel

router = APIRouter()


def _to_response(result) -> ActivityResponse:
    """Convierte ActivityResponseDTO → ActivityResponse Pydantic."""
    return ActivityResponse(
        id=str(result.id),
        title=result.title,
        day_of_april=result.day_of_april,
        time=result.time,
        priority_id=result.priority_id,
        priority_name=result.priority_name,
        priority_color=result.priority_color,
        description=result.description or "",
        emoji=result.emoji or "",
        completed=result.completed,
        has_image=result.has_image,
        image_path=result.image_path,
        checklist=[
            {"text": i.text, "done": i.done}
            for i in result.checklist
        ],
        checklist_done=result.checklist_done,
        checklist_total=result.checklist_total,
        created_at=str(result.created_at),
        updated_at=str(result.updated_at),
    )


def _translate_error(exc: Exception) -> HTTPException:
    import traceback
    with open("c:\\sgac\\error_log.txt", "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
    
    if isinstance(exc, ValidationError):
        return HTTPException(status_code=400, detail=str(exc))
    if isinstance(exc, UnauthorizedAccessError):
        return HTTPException(status_code=403, detail=str(exc))
    if isinstance(exc, (UserNotFoundError, ActivityNotFoundError)):
        return HTTPException(status_code=404, detail=str(exc))
    return HTTPException(status_code=500, detail=f"Error interno: {str(exc)}")


@router.get("", response_model=list[ActivityResponse])
async def list_activities(
    current_user: dict = Depends(get_current_user),
    activity_repo=Depends(get_activity_repository),
    user_repo=Depends(get_user_repository),
):
    try:
        use_case = GetAllAprilUseCase(activity_repo, user_repo)
        results = await use_case.execute(UUID(current_user["user_id"]), UUID(current_user["user_id"]))
        return [_to_response(r) for r in results]
    except Exception as exc:
        raise _translate_error(exc)


@router.get("/day/{day}", response_model=list[ActivityResponse])
async def get_activities_by_day(
    day: int = Path(..., ge=1, le=30),
    current_user: dict = Depends(get_current_user),
    activity_repo=Depends(get_activity_repository),
    user_repo=Depends(get_user_repository),
):
    try:
        use_case = GetByDayUseCase(activity_repo, user_repo)
        results = await use_case.execute(UUID(current_user["user_id"]), day)
        return [_to_response(r) for r in results]
    except Exception as exc:
        raise _translate_error(exc)


@router.get("/priority/{priority_id}", response_model=list[ActivityResponse])
async def get_activities_by_priority(
    priority_id: int,
    current_user: dict = Depends(get_current_user),
    activity_repo=Depends(get_activity_repository),
    user_repo=Depends(get_user_repository),
):
    try:
        use_case = FilterByPriorityUseCase(activity_repo, user_repo)
        results = await use_case.execute(UUID(current_user["user_id"]), priority_id)
        return [_to_response(r) for r in results]
    except Exception as exc:
        raise _translate_error(exc)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_activity(
    payload: ActivityCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    print(f"\n[SGAC] >>> PETICIÓN POST RECIBIDA - Usuario: {current_user.get('user_id')}")
    print(f"\n[SGAC] >>> CREANDO ACTIVIDAD para usuario: {current_user.get('user_id')}")
    try:
        now = datetime.now(timezone.utc)
        user_id = _uuid.UUID(str(current_user["user_id"]))

        checklist_data = []
        if payload.checklist:
            for item in payload.checklist:
                checklist_data.append({"text": str(item.text), "done": bool(item.done)})

        model = ActivityModel(
            id=_uuid.uuid4(),
            user_id=user_id,
            priority_id=int(payload.priority_id),
            day_of_april=int(payload.day),
            time=payload.time,
            title=str(payload.title),
            description=str(payload.description or ""),
            emoji=str(payload.emoji or ""),
            completed=False,
            has_image=False,
            image_path=None,
            checklist_json=_json.dumps(checklist_data),
            created_at=now,
            updated_at=now,
        )
        db.add(model)
        await db.commit()
        await db.refresh(model)

        priority_names = {1: "Baja", 2: "Media", 3: "Alta"}
        priority_colors = {1: "#22C55E", 2: "#F59E0B", 3: "#EF4444"}
        pid = model.priority_id

        checklist_out = []
        if model.checklist_json:
            try:
                checklist_out = _json.loads(model.checklist_json)
            except Exception:
                checklist_out = []

        return {
            "id": str(model.id),
            "title": str(model.title),
            "day_of_april": int(model.day_of_april),
            "time": model.time,
            "priority_id": int(pid),
            "priority_name": priority_names.get(pid, "Sin prioridad"),
            "priority_color": priority_colors.get(pid, "#6B7280"),
            "description": str(model.description or ""),
            "emoji": str(model.emoji or ""),
            "completed": bool(model.completed),
            "has_image": bool(model.has_image),
            "image_path": model.image_path,
            "checklist": checklist_out,
            "checklist_done": sum(1 for i in checklist_out if i.get("done")),
            "checklist_total": len(checklist_out),
            "created_at": model.created_at.isoformat() if model.created_at else "",
            "updated_at": model.updated_at.isoformat() if model.updated_at else "",
        }
    except Exception as exc:
        tb.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"{type(exc).__name__}: {str(exc)}"
        )


@router.put("/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: UUID,
    payload: ActivityUpdateRequest,
    current_user: dict = Depends(get_current_user),
    activity_repo=Depends(get_activity_repository),
    user_repo=Depends(get_user_repository),
):
    try:
        use_case = UpdateActivityUseCase(activity_repo, user_repo)
        dto = ActivityUpdateDTO(
            title=payload.title,
            time=payload.time,
            description=payload.description,
            priority_id=payload.priority_id,
            emoji=payload.emoji,
            completed=payload.completed,
            checklist=payload.checklist,
        )
        result = await use_case.execute(UUID(current_user["user_id"]), activity_id, dto)
        return _to_response(result)
    except Exception as exc:
        raise _translate_error(exc)


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: UUID,
    current_user: dict = Depends(get_current_user),
    activity_repo=Depends(get_activity_repository),
    user_repo=Depends(get_user_repository),
):
    try:
        use_case = DeleteActivityUseCase(activity_repo, user_repo)
        await use_case.execute(UUID(current_user["user_id"]), activity_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as exc:
        raise _translate_error(exc)
