from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import Notification, Task
from typing import List

from ..schemas import NotificationCreate, NotificationRead

router = APIRouter(prefix="/tasks/{task_id}/notifications", tags=["notifications"])


@router.post("/", response_model=NotificationRead, status_code=201)
def create_notification(
    task_id: int,
    payload: NotificationCreate,
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    note = Notification(
        task_id=task_id,
        notify_before_minutes=payload.notify_before_minutes
    )
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


@router.get("/", response_model=List[NotificationRead])
def read_notifications(
    task_id: int,
    session: Session = Depends(get_session)
):
    notes = session.exec(
        select(Notification).where(Notification.task_id == task_id)
    ).all()
    return notes
