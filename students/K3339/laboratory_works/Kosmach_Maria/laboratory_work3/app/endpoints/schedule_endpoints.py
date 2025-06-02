from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from db.connection import get_session
from model.models.models import DailySchedule
from model.schemas.daily_schedule import DailyScheduleRead, DailyScheduleCreate

schedule_router = APIRouter()


@schedule_router.post("/", response_model=DailyScheduleRead)
def create_schedule(schedule: DailyScheduleCreate, session: Session = Depends(get_session)):
    db_schedule = DailySchedule(**schedule.model_dump())
    session.add(db_schedule)
    session.commit()
    session.refresh(db_schedule)
    return db_schedule


@schedule_router.get("/", response_model=List[DailyScheduleRead])
def get_schedules(session: Session = Depends(get_session)):
    return session.exec(select(DailySchedule)).all()


@schedule_router.get("/{schedule_id}", response_model=DailyScheduleRead)
def get_schedule(schedule_id: int, session: Session = Depends(get_session)):
    schedule = session.get(DailySchedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@schedule_router.delete("/{schedule_id}", response_model=dict)
def delete_schedule(schedule_id: int, session: Session = Depends(get_session)):
    schedule = session.get(DailySchedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    session.delete(schedule)
    session.commit()
    return {"ok": True}
