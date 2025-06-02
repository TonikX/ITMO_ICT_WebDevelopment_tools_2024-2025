from typing import List

import aiohttp
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.celery_app import celery_app
from auth.auth import AuthHandler
from db.connection import get_session
from model.models.models import Task
from model.schemas.parse import ParseRequest
from model.schemas.task import TaskRead, TaskCreate, TaskUpdate

task_router = APIRouter()
auth_handler = AuthHandler()

@task_router.post("/parse")
async def parse(parse_request: ParseRequest):
    parser_url = "http://parser_app:8001/parse"
    async with aiohttp.ClientSession() as client:
        response = await client.post(parser_url, json=parse_request.model_dump(), timeout=15)
        response.raise_for_status()
        return await response.json()


@task_router.post("/parse-queue")
def start_parse(request: ParseRequest):
    task = celery_app.send_task("app.tasks.parse_url_task", args=[request.url])
    return {"task_id": task.id}


@task_router.get("/status/{task_id}")
def check_status(task_id: str):
    result = celery_app.AsyncResult(task_id)
    return {"status": result.status, "result": result.result}


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
