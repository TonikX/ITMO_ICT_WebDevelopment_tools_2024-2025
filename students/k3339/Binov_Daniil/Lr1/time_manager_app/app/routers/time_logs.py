from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from app.connection import get_session
from app.crud.time_logs import create_time_log, get_time_log, get_time_logs_by_task, update_time_log, delete_time_log
from app.schemas import TimeLogCreate, TimeLogRead
from app.routers.auth import get_current_user
from app.models import User
from app.crud.tasks import get_task

router = APIRouter(prefix="/time-logs", tags=["time_logs"])

@router.post("/", response_model=TimeLogRead)
def create_new_time_log(time_log: TimeLogCreate, task_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_task = get_task(session, task_id)
    if not db_task or db_task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this task")
    return create_time_log(session, time_log, task_id)

@router.get("/{time_log_id}", response_model=TimeLogRead)
def read_time_log(time_log_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_time_log = get_time_log(session, time_log_id)
    if not db_time_log:
        raise HTTPException(status_code=404, detail="TimeLog not found")
    if get_task(session, db_time_log.task_id).user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return db_time_log

@router.get("/task/{task_id}", response_model=List[TimeLogRead])
def read_time_logs_by_task(task_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_task = get_task(session, task_id)
    if not db_task or db_task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return get_time_logs_by_task(session, task_id)

@router.put("/{time_log_id}", response_model=TimeLogRead)
def update_existing_time_log(time_log_id: int, time_log_update: dict, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_time_log = get_time_log(session, time_log_id)
    if not db_time_log:
        raise HTTPException(status_code=404, detail="TimeLog not found")
    if get_task(session, db_time_log.task_id).user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    updated = update_time_log(session, time_log_id, time_log_update)
    return updated

@router.delete("/{time_log_id}")
def delete_existing_time_log(time_log_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_time_log = get_time_log(session, time_log_id)
    if not db_time_log:
        raise HTTPException(status_code=404, detail="TimeLog not found")
    if get_task(session, db_time_log.task_id).user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if not delete_time_log(session, time_log_id):
        raise HTTPException(status_code=404, detail="TimeLog not found")
    return {"message": "TimeLog deleted"}