from fastapi import FastAPI, Depends, APIRouter, HTTPException
from models.schedule import *
from connection import *
from sqlmodel import Session, select
from typing_extensions import TypedDict
from services.TaskService import get_todo_tasks
from services.TaskScheduleService import new_taskSchedule_create
from models.task_schedule import *
from datetime import datetime

def new_schedule_create(schedule: Schedule, session) -> Schedule:
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    return {"status": 200, "data": schedule}

def today_schedule_create(task_num: int, schedule: Schedule, session) -> Schedule:
    progress_tasks = get_todo_tasks(session)
    task_num = min(len(progress_tasks), task_num)
    
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    for todo_task in range(task_num):
        new_task = TaskSchedule(
            task_id=progress_tasks[todo_task].id,
            schedule_id=schedule.id,
            start_time=datetime.now()            
        )
        new_taskSchedule_create(new_task, session)    
    return {"status": 200, "data": schedule}



def list_all_schedules(session) -> List[Schedule]:
    return session.exec(select(Schedule)).all()


def get_schedule_by_id(schedule_id: int, session) -> Schedule:
    data = session.exec(select(Schedule).where(Schedule.id == schedule_id)).first()
    if not data:
        raise HTTPException(status_code=404, detail="Schedule not found")    
    return data

def delete_schedule(schedule_id: int, session):
    schedule = session.get(Schedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    session.delete(schedule)
    session.commit()
    return {"ok": True}    

def patch_schedule(schedule_id: int, schedule: Schedule, session) -> Schedule:
    db_schedule = session.get(Schedule, schedule_id)
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    schedule_data = schedule.model_dump(exclude_unset=True)
    for key, value in schedule_data.items():
        setattr(db_schedule, key, value)
    session.add(db_schedule)
    session.commit()
    session.refresh(db_schedule)
    return db_schedule