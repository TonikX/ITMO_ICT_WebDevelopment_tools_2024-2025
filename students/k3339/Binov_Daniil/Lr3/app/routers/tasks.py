from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from app.connection import get_session
from app.crud.tasks import create_task, get_task, get_tasks_by_user, update_task, delete_task
from app.schemas import TaskCreate, TaskRead
from app.routers.auth import get_current_user
from app.models import User
from celery_tasks import parse_and_save_task

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskRead)
def create_new_task(task: TaskCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return create_task(session, task, current_user.id)

@router.get("/{task_id}", response_model=TaskRead)
def read_task(task_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_task = get_task(session, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return db_task  

@router.get("/", response_model=List[TaskRead])
def read_tasks(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return get_tasks_by_user(session, current_user.id)

@router.put("/{task_id}", response_model=TaskRead)
def update_existing_task(task_id: int, task_update: dict, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    updated_task = update_task(session, task_id, task_update)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if updated_task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return updated_task

@router.delete("/{task_id}")
def delete_existing_task(task_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if not delete_task(session, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}

@router.post("/parse")
def parse_url(url: str, current_user: User = Depends(get_current_user)):
    task = parse_and_save_task.delay(url, current_user.id)
    return {"task_id": task.id, "message": "Parsing started asynchronously"}