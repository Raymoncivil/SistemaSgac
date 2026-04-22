"""
infrastructure/repositories/audit_repository_impl.py — Implementación del repositorio de auditoría.
"""

from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.interfaces.audit_repository import IAuditRepository
from domain.entities.audit_log import AuditLog
from infrastructure.database.models.audit_model import AuditLogModel


class AuditRepositoryImpl(IAuditRepository):
    """Repositorio de auditoría usando SQLAlchemy AsyncIO."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create(self, audit_log: AuditLog) -> AuditLog:
        model = AuditLogModel(
            id=audit_log.id,
            user_id=audit_log.user_id,
            action=audit_log.action,
            entity_type=audit_log.entity_type,
            entity_id=audit_log.entity_id,
            old_value=audit_log.old_value,
            new_value=audit_log.new_value,
            ip_address=audit_log.ip_address,
            created_at=audit_log.created_at,
        )
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return self._to_entity(model)

    async def get_all_logs(self) -> List[AuditLog]:
        query = select(AuditLogModel)
        result = await self.db.execute(query)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def get_logs_by_user(self, user_id: UUID) -> List[AuditLog]:
        query = select(AuditLogModel).where(AuditLogModel.user_id == user_id)
        result = await self.db.execute(query)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def get_logs_by_entity(self, entity_id: UUID) -> List[AuditLog]:
        query = select(AuditLogModel).where(AuditLogModel.entity_id == entity_id)
        result = await self.db.execute(query)
        return [self._to_entity(model) for model in result.scalars().all()]

    def _to_entity(self, model: AuditLogModel) -> AuditLog:
        return AuditLog(
            id=model.id,
            user_id=model.user_id,
            action=model.action,
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            old_value=model.old_value,
            new_value=model.new_value,
            ip_address=model.ip_address,
            created_at=model.created_at,
        )
