from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from ..database import AsyncSessionLocal
from ..models import Task, TimeEntry, Notification, PriorityEnum
from ..schemas import TaskCreate, TaskRead, TimeEntryRead, NotificationRead

router = APIRouter(prefix="/tasks", tags=["tasks"])


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/", response_model=List[TaskRead])
async def read_tasks(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Task))
    tasks = result.scalars().all()
    return tasks


@router.get("/{task_id}", response_model=TaskRead)
async def read_task(task_id: int, session: AsyncSession = Depends(get_session)):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate, session: AsyncSession = Depends(get_session)):
    task = Task(
        description=payload.description,
        due_date=payload.due_date,
        priority=PriorityEnum(payload.priority),
        user_id=payload.user_id,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(task_id: int, payload: TaskCreate, session: AsyncSession = Depends(get_session)):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    task.description = payload.description
    task.due_date = payload.due_date
    task.priority = PriorityEnum(payload.priority)
    task.user_id = payload.user_id
    await session.commit()
    await session.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, session: AsyncSession = Depends(get_session)):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    await session.delete(task)
    await session.commit()
    return None


@router.get("/{task_id}/entries", response_model=List[TimeEntryRead])
async def read_entries(task_id: int, session: AsyncSession = Depends(get_session)):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    result = await session.execute(select(TimeEntry).where(TimeEntry.task_id == task_id))
    entries = result.scalars().all()
    return entries


@router.post("/{task_id}/entries", response_model=TimeEntryRead, status_code=status.HTTP_201_CREATED)
async def create_entry(
    task_id: int,
    *,
    start_at: datetime,
    end_at: datetime,
    session: AsyncSession = Depends(get_session),
):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    duration_hours = (end_at - start_at).total_seconds() / 3600
    if duration_hours <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duration must be > 0. Check start_at and end_at."
        )

    entry = TimeEntry(
        task_id=task_id,
        start_at=start_at,
        end_at=end_at,
        duration=round(duration_hours, 2),
    )
    session.add(entry)

    # Note: If you have removed spent_time from Task model,
    # you can skip updating task.spent_time here.
    # If you have retained a spent_time field, update it:
    # task.spent_time = (task.spent_time or 0) + entry.duration
    # session.add(task)

    await session.commit()
    await session.refresh(entry)
    return entry


@router.get("/{task_id}/notifications", response_model=List[NotificationRead])
async def read_notifications(task_id: int, session: AsyncSession = Depends(get_session)):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    result = await session.execute(select(Notification).where(Notification.task_id == task_id))
    notes = result.scalars().all()
    return notes


@router.post("/{task_id}/notifications", response_model=NotificationRead, status_code=status.HTTP_201_CREATED)
async def create_notification(
    task_id: int,
    *,
    notify_before_minutes: int,
    session: AsyncSession = Depends(get_session),
):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    note = Notification(
        task_id=task_id,
        notify_before_minutes=notify_before_minutes
    )
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note
