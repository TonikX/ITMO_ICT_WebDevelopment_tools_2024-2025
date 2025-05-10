from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing_extensions import List

from db.connection import get_session
from model.models.models import Task
from model.schemas.task import TaskRead, TaskCreate, TaskUpdate

task_router = APIRouter()


@task_router.post("/", response_model=TaskRead, status_code=201)
def upload_task(data: TaskCreate, session: Session = Depends(get_session)):
    task = Task.model_validate(data)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@task_router.get("/", response_model=List[TaskRead])
def get_all_tasks(session: Session = Depends(get_session)):
    return session.exec(select(Task)).all()


@task_router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@task_router.post("/", response_model=TaskRead, status_code=201)
def create_task(data: TaskCreate, session: Session = Depends(get_session)):
    new_task = Task.model_validate(data)
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    return new_task


@task_router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, update: TaskUpdate, session: Session = Depends(get_session)):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    session.commit()
    session.refresh(db_task)
    return db_task


@task_router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(db_task)
    session.commit()
    return {"message": "Task deleted"}
