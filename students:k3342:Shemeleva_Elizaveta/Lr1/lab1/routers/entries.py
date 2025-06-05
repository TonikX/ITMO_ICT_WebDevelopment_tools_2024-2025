from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import TimeEntry, Task
from typing import List
from datetime import datetime
from auth import get_current_user


router = APIRouter(prefix="/tasks/{task_id}/entries", tags=["entries"])

@router.post("/")
def create_entry(
    task_id: int,
    start_at: datetime,
    end_at: datetime,
    duration: float,
    session: Session = Depends(get_session)
):
    # проверка: задача существует?
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    entry = TimeEntry(
        task_id=task_id,
        start_at=start_at,
        end_at=end_at,
        duration=duration
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.get("/", response_model=List[TimeEntry])
def read_entries(task_id: int, session: Session = Depends(get_session)):
    return session.exec(select(TimeEntry).where(TimeEntry.task_id == task_id)).all()
