"""
infrastructure/repositories/user_repository_impl.py — Implementación del repositorio de usuarios.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.interfaces.user_repository import IUserRepository
from domain.entities.user import User
from infrastructure.database.models.user_model import UserModel, UserRole


class UserRepositoryImpl(IUserRepository):
    """Repositorio de usuarios usando SQLAlchemy AsyncIO."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        model = await self.db.get(UserModel, user_id)
        return self._to_entity(model) if model else None

    async def get_by_rut(self, rut: str) -> Optional[User]:
        query = select(UserModel).where(UserModel.rut == rut)
        result = await self.db.execute(query)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all_users(self) -> List[User]:
        query = select(UserModel)
        result = await self.db.execute(query)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def create(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            rut=user.rut,
            full_name=user.full_name,
            password_hash=user.password_hash,
            role=UserRole(user.role),
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login,
        )
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return self._to_entity(model)

    async def update(self, user: User) -> User:
        model = await self.db.get(UserModel, user.id)
        if not model:
            raise ValueError(f"Usuario {user.id} no encontrado")

        model.full_name = user.full_name
        model.rut = user.rut
        model.password_hash = user.password_hash
        model.role = UserRole(user.role)
        model.is_active = user.is_active
        model.last_login = user.last_login

        await self.db.commit()
        await self.db.refresh(model)
        return self._to_entity(model)

    async def delete(self, user_id: UUID) -> bool:
        model = await self.db.get(UserModel, user_id)
        if not model:
            return False
        await self.db.delete(model)
        await self.db.commit()
        return True

    async def update_last_login(self, user_id: UUID) -> None:
        model = await self.db.get(UserModel, user_id)
        if not model:
            return
        model.last_login = datetime.utcnow()
        await self.db.commit()

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            rut=model.rut,
            full_name=model.full_name,
            password_hash=model.password_hash,
            role=model.role.value,
            is_active=model.is_active,
            created_at=model.created_at,
            last_login=model.last_login,
        )
