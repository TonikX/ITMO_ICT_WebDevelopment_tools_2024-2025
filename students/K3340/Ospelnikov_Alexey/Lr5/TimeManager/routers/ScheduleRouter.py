from fastapi import FastAPI, Depends, APIRouter
from models.user import *
from connection import *
from sqlmodel import Session, select
from typing_extensions import TypedDict
from schemas.schedule_schema import *
from models.schedule import *
from services.ScheduleService import *


scheduleRouter = APIRouter(
    prefix="/schedule", tags=['Schedule']
)

@scheduleRouter.get("/schedule_list", response_model=List[ScheduleRead])
def schedules_list(session=Depends(get_session)) -> List[Schedule]:
    return list_all_schedules(session)


@scheduleRouter.get("/{schedule_id}", response_model=ScheduleRead)
def schedules_get(schedule_id: int, session=Depends(get_session)) -> Schedule:
    return get_schedule_by_id(schedule_id, session)


@scheduleRouter.post("/")
def schedule_create(schedule: Schedule, session=Depends(get_session)) -> TypedDict('Response', { "status": int, "data": Schedule }):
    data = new_schedule_create(schedule, session)
    return {"status": 200, "data": data}

@scheduleRouter.post("/today")
def schedule_create_today(task_num: int, 
                          schedule: Schedule, 
                          session=Depends(get_session)) -> TypedDict('Response', { "status": int, "data": Schedule }):
    data = today_schedule_create(task_num, schedule, session)
    return {"status": 200, "data": data}


@scheduleRouter.delete("/delete{schedule_id}")
def schedule_delete(schedule_id: int, session=Depends(get_session)):
    return delete_schedule(schedule_id, session)
    
    
@scheduleRouter.patch("/{schedule_id}")
def schedule_update(schedule_id: int, schedule: Schedule, session=Depends(get_session)) -> Schedule:
    db_schedule = patch_schedule(schedule_id, schedule, session)
    return db_schedule