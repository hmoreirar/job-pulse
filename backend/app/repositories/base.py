import uuid
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import select, func, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class RepositoryBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: uuid.UUID) -> ModelType | None:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        stmt = select(func.count()).select_from(self.model)
        result = await self.db.execute(stmt)
        return result.scalar()

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: uuid.UUID) -> bool:
        stmt = sa_delete(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount > 0
