from sqlmodel import Session, select
from typing import Optional, List
from app.models import TimeLog
from app.schemas import TimeLogCreate, TimeLogRead
from datetime import datetime

def create_time_log(session: Session, time_log: TimeLogCreate, task_id: int) -> TimeLog:
    db_time_log = TimeLog(**time_log.dict(), task_id=task_id)
    if time_log.end_time:
        delta = time_log.end_time - time_log.start_time
        db_time_log.duration = int(delta.total_seconds() / 60)  # В минутах
    session.add(db_time_log)
    session.commit()
    session.refresh(db_time_log)
    return db_time_log

def get_time_log(session: Session, time_log_id: int) -> Optional[TimeLog]:
    return session.get(TimeLog, time_log_id)

def get_time_logs_by_task(session: Session, task_id: int) -> List[TimeLog]:
    statement = select(TimeLog).where(TimeLog.task_id == task_id)
    return session.exec(statement).all()

def update_time_log(session: Session, time_log_id: int, time_log_update: dict) -> Optional[TimeLog]:
    db_time_log = get_time_log(session, time_log_id)
    if not db_time_log:
        return None
    for key, value in time_log_update.items():
        setattr(db_time_log, key, value)
    if 'end_time' in time_log_update and db_time_log.end_time:
        delta = db_time_log.end_time - db_time_log.start_time
        db_time_log.duration = int(delta.total_seconds() / 60)
    session.add(db_time_log)
    session.commit()
    session.refresh(db_time_log)
    return db_time_log

def delete_time_log(session: Session, time_log_id: int) -> bool:
    db_time_log = get_time_log(session, time_log_id)
    if not db_time_log:
        return False
    session.delete(db_time_log)
    session.commit()
    return True