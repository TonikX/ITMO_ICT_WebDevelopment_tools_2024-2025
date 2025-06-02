from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from auth.auth import AuthHandler
from db.connection import get_session
from model.models.models import Task
from model.schemas.task import TaskRead, TaskCreate, TaskUpdate

task_router = APIRouter()
auth_handler = AuthHandler()


@task_router.post("/", response_model=TaskRead)
def create_task(task: TaskCreate, session: Session = Depends(get_session),
                current_user=Depends(auth_handler.get_current_user)):
    db_task = Task(**task.model_dump(), owner_id=current_user.id)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@task_router.get("/", response_model=List[TaskRead])
def get_tasks(session: Session = Depends(get_session)):
    return session.exec(select(Task)).all()


@task_router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@task_router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, update: TaskUpdate, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    session.commit()
    session.refresh(task)
    return task


@task_router.delete("/{task_id}", response_model=dict)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}
