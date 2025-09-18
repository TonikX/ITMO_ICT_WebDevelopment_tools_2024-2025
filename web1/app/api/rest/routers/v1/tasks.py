from fastapi import Depends, APIRouter
from app.controolers import task_controller
from app.auth import auth_handler
from database import get_session
from app.models import *

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/get-all", response_model=list[Task])
def get_all(session=Depends(get_session)):
    return task_controller.get_all_tasks(session)

@router.get("/get-one/{task_id}", response_model=TaskFull)
def get_one(task_id: int, session=Depends(get_session)):
    return task_controller.get_task_by_id(task_id, session)

@router.post("/create", response_model=TaskFull)
def create(task_data: TaskCreate, authUserId=Depends(auth_handler.get_user), session=Depends(get_session)):
    return task_controller.create_task(task_data, authUserId, session)

@router.patch("/update/{task_id}", response_model=TaskFull)
def update(task_id: int, updates: TaskUpdate, authUserId=Depends(auth_handler.get_user), session=Depends(get_session)):
    return task_controller.update_task(task_id, updates, authUserId, session)

@router.delete("/delete-task/{task_id}")
def delete(task_id: int, authUserId=Depends(auth_handler.get_user), session=Depends(get_session)):
    return task_controller.delete_task(task_id, authUserId, session)
