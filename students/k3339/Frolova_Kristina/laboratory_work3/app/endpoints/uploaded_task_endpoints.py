from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db.connection import get_session
from model.models.models import UploadedTask
from model.schemas.uploaded_task import UploadedTaskRead, UploadedTaskCreate, UploadedTaskUpdate

uploaded_task_router = APIRouter()


@uploaded_task_router.post("/", response_model=UploadedTaskRead, status_code=201)
def upload_task(uploaded_task: UploadedTaskCreate, session: Session = Depends(get_session)):
    task = UploadedTask.model(uploaded_task)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@uploaded_task_router.get("/", response_model=List[UploadedTaskRead])
def get_all_uploaded_tasks(session: Session = Depends(get_session)):
    return session.exec(select(UploadedTask)).all()


@uploaded_task_router.get("/{uploaded_task_id}", response_model=UploadedTaskRead)
def get_uploaded_task(uploaded_task_id: int, session: Session = Depends(get_session)):
    task = session.get(UploadedTask, uploaded_task_id)
    if not task:
        raise HTTPException(status_code=404, detail="UploadedTask not found")
    return task


@uploaded_task_router.post("/", response_model=UploadedTaskRead, status_code=201)
def create_uploaded_task(uploaded_task: UploadedTaskCreate, session: Session = Depends(get_session)):
    new_task = UploadedTask.model_validate(uploaded_task)
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    return new_task


@uploaded_task_router.patch("/{uploaded_task_id}", response_model=UploadedTaskRead)
def update_uploaded_task(uploaded_task_id: int, update: UploadedTaskUpdate, session: Session = Depends(get_session)):
    db_task = session.get(UploadedTask, uploaded_task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="UploadedTask not found")
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    session.commit()
    session.refresh(db_task)
    return db_task


@uploaded_task_router.delete("/{uploaded_task_id}", status_code=204)
def delete_uploaded_task(uploaded_task_id: int, session: Session = Depends(get_session)):
    db_task = session.get(UploadedTask, uploaded_task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="UploadedTask not found")
    session.delete(db_task)
    session.commit()
    return {"message": "UploadedTask deleted"}
