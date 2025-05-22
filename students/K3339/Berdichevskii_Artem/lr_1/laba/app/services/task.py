from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task
from app.repositories.task import task_repository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    async def create_task(
            self,
            db: AsyncSession,
            task_data: TaskCreate,
            event_id: int
    ) -> Task:
        data = task_data.model_dump()
        data['event_id'] = event_id
        task = await task_repository.create(db, Task(**data))
        return task

    async def get_tasks(
            self,
            db: AsyncSession,
            skip: int = 0,
            limit: int = 100
    ) -> List[Task]:
        tasks = await task_repository.get_all(db, skip=skip, limit=limit)
        return tasks

    async def get_task_by_id(
            self,
            db: AsyncSession,
            task_id: int
    ) -> Task:
        task = await task_repository.get(db, task_id)
        return task

    async def get_task_by_event(
            self,
            db: AsyncSession,
            event_id: int
    ) -> List[Task]:
        tasks = await task_repository.get_by_event_id(db, event_id)
        return tasks

    async def update_task(
            self,
            db: AsyncSession,
            updated_task: TaskUpdate
    ):
        await task_repository.update(db, updated_task)
        return updated_task


task_service = TaskService()
