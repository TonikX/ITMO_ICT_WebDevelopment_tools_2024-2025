from fastapi import FastAPI, Depends, APIRouter, HTTPException
from models.task import *
from connection import *
from sqlmodel import Session, select
from typing_extensions import TypedDict


def new_task_create(task: Task, session) -> Task:
    session.add(task)
    session.commit()
    session.refresh(task)
    return {"status": 200, "data": task}


def list_all_tasks(session) -> List[Task]:
    return session.exec(select(Task)).all()


def get_task_by_id(task_id: int, session) -> Task:
    task = session.exec(select(Task).where(Task.id == task_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")    
    return task

def get_todo_tasks(session) -> Task:
    
    return session.exec(select(Task).where(Task.status == "in_progress")).all()

def delete_task(task_id: int, session):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}    

def patch_task(task_id: int, task: Task, session) -> Task:
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_data = task.model_dump(exclude_unset=True)
    for key, value in task_data.items():
        setattr(db_task, key, value)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task