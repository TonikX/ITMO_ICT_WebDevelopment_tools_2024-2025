from fastapi import FastAPI, Depends, APIRouter
from models.task import *
from connection import *
from sqlmodel import Session, select
from typing_extensions import TypedDict
from services.TaskService import *
from schemas.task_schema import TaskCreate, TaskRead

taskRouter = APIRouter(
    prefix="/task", tags=['Task']
)


@taskRouter.get("/task_list", response_model=List[TaskRead])
def tasks_list(session=Depends(get_session)) -> List[Task]:
    return list_all_tasks(session)

@taskRouter.get("/todo_task_list", response_model=List[TaskRead])
def todo_tasks_list(session=Depends(get_session)) -> List[Task]:
    return get_todo_tasks(session)

@taskRouter.get("/{task_id}", response_model=TaskUser)
def tasks_get(task_id: int, session=Depends(get_session)) -> Task:
    return get_task_by_id(task_id, session)


@taskRouter.post("/")
def task_create(task: Task, session=Depends(get_session)) -> TypedDict('Response', { "status": int, "data": Task }):
    data = new_task_create(task, session)
    return {"status": 200, "data": task}



@taskRouter.delete("/delete{task_id}")
def task_delete(task_id: int, session=Depends(get_session)):
    return delete_task(task_id, session)
    
    
@taskRouter.patch("/{task_id}")
def task_update(task_id: int, task: Task, session=Depends(get_session)) -> Task:
    db_task = patch_task(task_id, task, session)
    return db_task

