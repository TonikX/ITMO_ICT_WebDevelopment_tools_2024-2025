from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.api.v1.endpoints.submissions import task_submission_router
from app.database import get_db
from app.schemas.task import TaskDisplay, TaskCreate
from app.schemas.user import UserInDB
from app.services.task import task_service

event_attached_router = APIRouter(prefix='/{event_id}/tasks', tags=['tasks'])


@event_attached_router.get('/', response_model=List[TaskDisplay])
async def get_event_tasks(
        event_id: int,
        db: AsyncSession = Depends(get_db),
):
    return await task_service.get_task_by_event(db, event_id)


@event_attached_router.post('/', response_model=TaskDisplay)
async def create_task(
        task_data: TaskCreate,
        event_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserInDB = Depends(get_current_active_user),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    task = await task_service.create_task(db, task_data, event_id)
    return task


router = APIRouter(prefix='/tasks', tags=['tasks'])
router.include_router(task_submission_router)


@router.get('/', response_model=List[TaskDisplay])
async def get_tasks(
        db: AsyncSession = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
):
    tasks = await task_service.get_tasks(db, skip=skip, limit=limit)

    return tasks


@router.get('/{task_id}', response_model=TaskDisplay)
async def get_task(
        task_id: int,
        db: AsyncSession = Depends(get_db),
):
    return await task_service.get_task_by_id(db, task_id)
