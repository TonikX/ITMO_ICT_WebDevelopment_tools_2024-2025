from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import Task
from app.repositories.base import BaseRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskRepository(BaseRepository[Task, TaskCreate, TaskUpdate]):
    async def get_by_event_id(
            self,
            db: AsyncSession,
            event_id: int,
    ):
        statement = select(Task).filter(Task.event_id == event_id)
        results = await db.execute(statement)
        return results.scalars().all()


task_repository = TaskRepository(Task)
