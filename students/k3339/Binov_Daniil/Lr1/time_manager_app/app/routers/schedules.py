from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from app.connection import get_session
from app.crud.schedules import create_schedule, get_schedule, get_schedules_by_user, update_schedule, delete_schedule
from app.schemas import ScheduleCreate, ScheduleRead
from app.routers.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/schedules", tags=["schedules"])

@router.post("/", response_model=ScheduleRead)
def create_new_schedule(schedule: ScheduleCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return create_schedule(session, schedule, current_user.id)

@router.get("/{schedule_id}", response_model=ScheduleRead)
def read_schedule(schedule_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_schedule = get_schedule(session, schedule_id)
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    if db_schedule.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return db_schedule

@router.get("/", response_model=List[ScheduleRead])
def read_schedules(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return get_schedules_by_user(session, current_user.id)

@router.put("/{schedule_id}", response_model=ScheduleRead)
def update_existing_schedule(schedule_id: int, schedule_update: dict, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_schedule = get_schedule(session, schedule_id)
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    if db_schedule.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    updated = update_schedule(session, schedule_id, schedule_update)
    return updated

@router.delete("/{schedule_id}")
def delete_existing_schedule(schedule_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_schedule = get_schedule(session, schedule_id)
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    if db_schedule.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if not delete_schedule(session, schedule_id):
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"message": "Schedule deleted"}