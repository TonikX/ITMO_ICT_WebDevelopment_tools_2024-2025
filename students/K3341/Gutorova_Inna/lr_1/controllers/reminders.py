from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from models import Reminder, ReminderCreate, ReminderRead, Task
from connection import get_session
from auth.auth import auth_service
from models import User

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.post("/", response_model=ReminderRead)
def create_reminder(
        reminder: ReminderCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(auth_service.get_current_user)
):
    task = session.get(Task, reminder.task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    db_reminder = Reminder.from_orm(reminder)
    session.add(db_reminder)
    session.commit()
    session.refresh(db_reminder)
    return db_reminder


@router.get("/", response_model=List[ReminderRead])
def read_reminders(
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session),
        current_user: User = Depends(auth_service.get_current_user)
):
    reminders = session.exec(
        select(Reminder)
        .join(Task)
        .where(Task.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    ).all()
    return reminders


@router.get("/{reminder_id}", response_model=ReminderRead)
def read_reminder(
        reminder_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(auth_service.get_current_user)
):
    reminder = session.get(Reminder, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    task = session.get(Task, reminder.task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    return reminder


@router.delete("/{reminder_id}")
def delete_reminder(
        reminder_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(auth_service.get_current_user)
):
    reminder = session.get(Reminder, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    task = session.get(Task, reminder.task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(reminder)
    session.commit()
    return {"message": "Reminder deleted successfully"}