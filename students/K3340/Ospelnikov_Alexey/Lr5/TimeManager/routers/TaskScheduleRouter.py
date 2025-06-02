from fastapi import FastAPI, Depends, APIRouter
from models.task_schedule import *
from connection import *
from sqlmodel import Session, select
from typing_extensions import TypedDict
from services.TaskScheduleService import *

from schemas.task_schedule_schema import *


taskScheduleRouter = APIRouter(
    prefix="/task_schedule", tags=['TaskSchedule']
)

@taskScheduleRouter.get("/{task_schedule_id}", response_model=TaskScheduleSerializator)
def tasks_schedule_get(task_schedule_id: int, 
                       session=Depends(get_session)) -> TaskSchedule:
    task_schedule = session.get(TaskSchedule, task_schedule_id)
    return task_schedule

@taskScheduleRouter.post("/")
def taskSchedule_create(taskSchedule: TaskSchedule, session=Depends(get_session)) -> TypedDict('Response', { "status": int, "data": TaskSchedule }):
    data = new_taskSchedule_create(taskSchedule, session)
    return {"status": 200, "data": taskSchedule}



@taskScheduleRouter.delete("/delete{taskSchedule_id}")
def taskSchedule_delete(taskSchedule_id: int, session=Depends(get_session)):
    return delete_taskSchedule(taskSchedule_id, session)
    
    
@taskScheduleRouter.patch("/{taskSchedule_id}")
def taskSchedule_update(taskSchedule_id: int, taskSchedule: TaskSchedule, session=Depends(get_session)) -> TaskSchedule:
    db_taskSchedule = patch_taskSchedule(taskSchedule_id, taskSchedule, session)
    return db_taskSchedule

