from sqlmodel import Session, select
from typing import Optional, List
from app.models import Schedule
from app.schemas import ScheduleCreate, ScheduleRead

def create_schedule(session: Session, schedule: ScheduleCreate, user_id: int) -> Schedule:
    db_schedule = Schedule(**schedule.dict(), user_id=user_id)
    session.add(db_schedule)
    session.commit()
    session.refresh(db_schedule)
    return db_schedule

def get_schedule(session: Session, schedule_id: int) -> Optional[Schedule]:
    return session.get(Schedule, schedule_id)

def get_schedules_by_user(session: Session, user_id: int) -> List[Schedule]:
    statement = select(Schedule).where(Schedule.user_id == user_id)
    return session.exec(statement).all()

def update_schedule(session: Session, schedule_id: int, schedule_update: dict) -> Optional[Schedule]:
    db_schedule = get_schedule(session, schedule_id)
    if not db_schedule:
        return None
    for key, value in schedule_update.items():
        setattr(db_schedule, key, value)
    session.add(db_schedule)
    session.commit()
    session.refresh(db_schedule)
    return db_schedule

def delete_schedule(session: Session, schedule_id: int) -> bool:
    db_schedule = get_schedule(session, schedule_id)
    if not db_schedule:
        return False
    session.delete(db_schedule)
    session.commit()
    return True