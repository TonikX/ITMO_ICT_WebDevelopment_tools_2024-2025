from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db.connection import get_session
from models.models import TimeLog
from models.timelog import TimeLogCreate, TimeLogRead

timelog_router = APIRouter(prefix="/timelogs", tags=["TimeLogs"])


@timelog_router.post("/", response_model=TimeLogRead)
def create_log(log: TimeLogCreate, session: Session = Depends(get_session)):
    db_log = TimeLog(**log.dict())
    session.add(db_log)
    session.commit()
    session.refresh(db_log)
    return db_log


@timelog_router.get("/task/{task_id}", response_model=list[TimeLogRead])
def get_logs_for_task(task_id: int, session: Session = Depends(get_session)):
    return session.exec(select(TimeLog).where(TimeLog.task_id == task_id)).all()
