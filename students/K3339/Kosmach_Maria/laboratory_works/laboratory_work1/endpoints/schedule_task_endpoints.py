from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from db.connection import get_session
from model.models.models import ScheduleTask
from model.schemas.schedule_task import ScheduleTaskRead, ScheduleTaskCreate

schedule_task_router = APIRouter()


@schedule_task_router.post("/", response_model=ScheduleTaskRead)
def create_schedule_task(item: ScheduleTaskCreate, session: Session = Depends(get_session)):
    schedule_task = ScheduleTask(**item.model_dump())
    session.add(schedule_task)
    session.commit()
    session.refresh(schedule_task)
    return schedule_task


@schedule_task_router.get("/", response_model=List[ScheduleTaskRead])
def get_schedule_tasks(session: Session = Depends(get_session)):
    return session.exec(select(ScheduleTask)).all()


@schedule_task_router.get("/{schedule_id}/{task_id}", response_model=ScheduleTaskRead)
def get_schedule_task(schedule_id: int, task_id: int, session: Session = Depends(get_session)):
    item = session.get(ScheduleTask, (schedule_id, task_id))
    if not item:
        raise HTTPException(status_code=404, detail="ScheduleTask not found")
    return item


@schedule_task_router.delete("/{schedule_id}/{task_id}", response_model=dict)
def delete_schedule_task(schedule_id: int, task_id: int, session: Session = Depends(get_session)):
    item = session.get(ScheduleTask, (schedule_id, task_id))
    if not item:
        raise HTTPException(status_code=404, detail="ScheduleTask not found")
    session.delete(item)
    session.commit()
    return {"ok": True}
