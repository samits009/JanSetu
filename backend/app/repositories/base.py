from typing import Generic, TypeVar, Type, Any, Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, **kwargs) -> ModelType:
        db_obj = self.model(**kwargs)
        self.session.add(db_obj)
        await self.session.flush()
        return db_obj

    async def update(self, db_obj: ModelType, **kwargs) -> ModelType:
        for key, value in kwargs.items():
            setattr(db_obj, key, value)
        self.session.add(db_obj)
        await self.session.flush()
        return db_obj

    async def delete(self, id: Any) -> bool:
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def soft_delete(self, db_obj: ModelType) -> ModelType:
        from sqlalchemy.sql import func
        db_obj.deleted_at = func.now()
        self.session.add(db_obj)
        await self.session.flush()
        return db_obj
