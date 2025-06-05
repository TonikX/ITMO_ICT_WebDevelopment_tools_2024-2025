from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import TimeEntry, Task
from typing import List
from datetime import datetime

from ..schemas import TimeEntryCreate, TimeEntryRead

router = APIRouter(prefix="/tasks/{task_id}/entries", tags=["entries"])


@router.post("/", response_model=TimeEntryRead, status_code=201)
def create_entry(
    task_id: int,
    payload: TimeEntryCreate,
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    duration_hours = (payload.end_at - payload.start_at).total_seconds() / 3600
    if duration_hours <= 0:
        raise HTTPException(
            status_code=400,
            detail="Duration must be > 0. Check start_at and end_at."
        )

    entry = TimeEntry(
        task_id=task_id,
        start_at=payload.start_at,
        end_at=payload.end_at,
        duration=round(duration_hours, 2),
    )
    session.add(entry)

    task.spent_time += entry.duration
    session.add(task)

    session.commit()
    session.refresh(entry)
    return entry


@router.get("/", response_model=List[TimeEntryRead])
def read_entries(
    task_id: int,
    session: Session = Depends(get_session)
):
    entries = session.exec(
        select(TimeEntry).where(TimeEntry.task_id == task_id)
    ).all()
    return entries
