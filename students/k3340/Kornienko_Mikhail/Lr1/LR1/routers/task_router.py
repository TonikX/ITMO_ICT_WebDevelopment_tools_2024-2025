from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from typing import List
from connection import get_session
from util.auth import authenticate_user
from models.task_model import Task, TaskCreate, TaskWithFullDetails
from models.user_model import User

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=Task)
def create_task(task: TaskCreate, current_user: User = Depends(authenticate_user), session=Depends(get_session)):
    if not current_user.is_organizer:
        raise HTTPException(status_code=403, detail="Only organizers can create tasks")
    new_task = Task(**task.dict(), user_id=current_user.id)
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    return new_task


@router.get("/", response_model=List[TaskWithFullDetails])
def list_tasks(session=Depends(get_session)):
    return session.exec(select(Task)).all()


@router.get("/{task_id}", response_model=TaskWithFullDetails)
def get_task(task_id: int, session=Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
