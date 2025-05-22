from typing import Any, Generic, TypeVar, List

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ModelType]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        for field in obj_in.model_dump(exclude_unset=True):
            setattr(db_obj, field, getattr(obj_in, field))
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: int) -> ModelType | None:
        db_obj = await self.get(db, id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
        return db_obj
