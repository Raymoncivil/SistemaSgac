
"""
infrastructure/repositories/activity_repository_impl.py — Implementación concreta del repositorio de actividades.
"""

import json
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.interfaces.activity_repository import IActivityRepository
from domain.entities.activity import Activity, ChecklistItem
from infrastructure.database.models.activity_model import ActivityModel


class ActivityRepositoryImpl(IActivityRepository):
    """Repositorio de actividades usando SQLAlchemy AsyncIO."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_by_id(self, activity_id: UUID) -> Optional[Activity]:
        model = await self.db.get(ActivityModel, activity_id)
        return self._to_entity(model) if model else None

    async def get_by_user_and_day(self, user_id: UUID, day: int) -> List[Activity]:
        query = select(ActivityModel).where(
            ActivityModel.user_id == user_id,
            ActivityModel.day_of_april == day
        )
        result = await self.db.execute(query)
        return [self._to_entity(row[0]) for row in result.fetchall()]

    async def get_all_by_user(self, user_id: UUID) -> List[Activity]:
        query = select(ActivityModel).where(ActivityModel.user_id == user_id)
        result = await self.db.execute(query)
        return [self._to_entity(row[0]) for row in result.fetchall()]

    async def get_by_user_and_priority(self, user_id: UUID, priority_id: int) -> List[Activity]:
        query = select(ActivityModel).where(
            ActivityModel.user_id == user_id,
            ActivityModel.priority_id == priority_id
        )
        result = await self.db.execute(query)
        return [self._to_entity(row[0]) for row in result.fetchall()]

    async def get_all_for_admin(self) -> List[Activity]:
        query = select(ActivityModel)
        result = await self.db.execute(query)
        return [self._to_entity(row[0]) for row in result.fetchall()]

    async def create(self, activity: Activity) -> Activity:
        model = self._to_model(activity)
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return self._to_entity(model)

    async def update(self, activity: Activity) -> Activity:
        model = await self.db.get(ActivityModel, activity.id)
        if not model:
            raise ValueError(f"Actividad {activity.id} no encontrada")

        model.priority_id = activity.priority_id
        model.title = activity.title
        model.description = activity.description
        model.emoji = activity.emoji
        model.completed = activity.completed
        model.has_image = activity.has_image
        model.image_path = activity.image_path
        model.checklist_json = json.dumps([
            {"text": item.text, "done": item.done}
            for item in activity.checklist
        ])
        model.updated_at = activity.updated_at

        await self.db.commit()
        await self.db.refresh(model)
        return self._to_entity(model)

    async def delete(self, activity_id: UUID) -> bool:
        model = await self.db.get(ActivityModel, activity_id)
        if not model:
            return False
        await self.db.delete(model)
        await self.db.commit()
        return True

    def _to_entity(self, model: ActivityModel) -> Activity:
        checklist = []
        if model.checklist_json:
            try:
                checklist_data = json.loads(model.checklist_json)
                checklist = [
                    ChecklistItem(
                        text=item.get("text", ""),
                        done=item.get("done", False)
                    )
                    for item in checklist_data
                ]
            except (ValueError, TypeError):
                checklist = []

        return Activity(
            id=model.id,
            user_id=model.user_id,
            priority_id=model.priority_id,
            day_of_april=model.day_of_april,
            title=model.title,
            description=model.description,
            emoji=model.emoji,
            completed=model.completed,
            has_image=model.has_image,
            image_path=model.image_path,
            checklist=checklist,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, activity: Activity) -> ActivityModel:
        return ActivityModel(
            id=activity.id,
            user_id=activity.user_id,
            priority_id=activity.priority_id,
            day_of_april=activity.day_of_april,
            title=activity.title,
            description=activity.description,
            emoji=activity.emoji,
            completed=activity.completed,
            has_image=activity.has_image,
            image_path=activity.image_path,
            checklist_json=json.dumps([
                {"text": item.text, "done": item.done}
                for item in activity.checklist
            ]),
            created_at=activity.created_at,
            updated_at=activity.updated_at,
        )