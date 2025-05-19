from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from database import get_session
from sqlmodel import Session
from auth import get_current_user

from models import Task, TimeEntry, Notification
from models import PriorityEnum
from datetime import datetime

router = APIRouter()

#Задачи
@router.get("/", response_model=List[Task])
def read_tasks(session: Session = Depends(get_session)):
    return session.exec(select(Task)).all()


@router.get("/{task_id}", response_model=Task)
def read_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/", response_model=Task, status_code=201)
def create_task(
    *,
    session: Session = Depends(get_session),
    description: str,
    due_date: datetime,
    priority: PriorityEnum
):
    task = Task(
        description=description,
        due_date=due_date,
        priority=priority,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.patch("/{task_id}", response_model=Task)
def update_task(
    *,
    task_id: int,
    session: Session = Depends(get_session),
    description: Optional[str] = None,
    due_date: Optional[datetime] = None,
    priority: Optional[PriorityEnum] = None,
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if description is not None:
        task.description = description
    if due_date is not None:
        task.due_date = due_date
    if priority is not None:
        task.priority = priority
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return


#Интервалы времени (otm)
@router.get("/{task_id}/entries", response_model=List[TimeEntry])
def read_entries(task_id: int, session: Session = Depends(get_session)):
    return session.exec(
        select(TimeEntry).where(TimeEntry.task_id == task_id)
    ).all()


@router.post("/{task_id}/entries", response_model=TimeEntry, status_code=201)
def create_entry(
    *,
    task_id: int,
    session: Session = Depends(get_session),
    start_at: datetime,
    end_at: datetime,
):
    task = session.get(Task, task_id)
    # проверяем, что задача существует
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # вычисляем продолжительность
    duration_hours = (end_at - start_at).total_seconds() / 3600

    if duration_hours <= 0:
        raise HTTPException(
            status_code=400,
            detail="Duration must be >0. Check start and end times."
        )

    entry = TimeEntry(
        task_id=task_id,
        start_at=start_at,
        end_at=end_at,
        duration=round(duration_hours, 2),
    )
    session.add(entry)

    # обновляем общее время
    task.spent_time += entry.duration
    session.add(task)

    session.commit()
    session.refresh(entry)
    return entry


# Уведомления (otm)
@router.get("/{task_id}/notifications", response_model=List[Notification])
def read_notifications(task_id: int, session: Session = Depends(get_session)):
    return session.exec(
        select(Notification).where(Notification.task_id == task_id)
    ).all()


@router.post("/{task_id}/notifications", response_model=Notification, status_code=201)
def create_notification(
    *,
    task_id: int,
    session: Session = Depends(get_session),
    notify_before_minutes: int
):
    if not session.get(Task, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    note = Notification(task_id=task_id, notify_before_minutes=notify_before_minutes)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note
