from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from db.connection import get_session
from model.models.models import TimeLog
from model.schemas.time_log import TimeLogRead, TimeLogCreate

timelog_router = APIRouter()


@timelog_router.post("/", response_model=TimeLogRead)
def create_timelog(log: TimeLogCreate, session: Session = Depends(get_session)):
    db_log = TimeLog(**log.model_dump())
    session.add(db_log)
    session.commit()
    session.refresh(db_log)
    return db_log


@timelog_router.get("/", response_model=List[TimeLogRead])
def get_timelogs(session: Session = Depends(get_session)):
    return session.exec(select(TimeLog)).all()


@timelog_router.get("/{log_id}", response_model=TimeLogRead)
def get_timelog(log_id: int, session: Session = Depends(get_session)):
    log = session.get(TimeLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="TimeLog not found")
    return log


@timelog_router.delete("/{log_id}", response_model=dict)
def delete_timelog(log_id: int, session: Session = Depends(get_session)):
    log = session.get(TimeLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="TimeLog not found")
    session.delete(log)
    session.commit()
    return {"ok": True}
