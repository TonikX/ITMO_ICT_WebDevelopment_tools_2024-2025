from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Notification, Task
from typing import List
from datetime import datetime

router = APIRouter(prefix="/tasks/{task_id}/notifications", tags=["notifications"])

@router.post("/")
def create_notification(
    task_id: int,
    message: str,
    notify_at: datetime,
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    notification = Notification(
        task_id=task_id,
        message=message,
        notify_at=notify_at
    )
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification


@router.get("/", response_model=List[Notification])
def read_notifications(task_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Notification).where(Notification.task_id == task_id)).all()
