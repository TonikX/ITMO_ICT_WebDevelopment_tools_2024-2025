from typing import Optional, List
from fastapi import FastAPI, Depends, APIRouter, HTTPException

from datetime import datetime
from models.task_schedule import *

from sqlmodel import SQLModel, Field, Relationship, Column, TIMESTAMP, text
	
def new_taskSchedule_create(taskSchedule: TaskSchedule, session) -> TaskSchedule:
    session.add(taskSchedule)
    session.commit()
    session.refresh(taskSchedule)
    return {"status": 200, "data": taskSchedule}


def get_taskSchedule_by_id(taskSchedule_id: int, session) -> TaskSchedule:
    taskSchedule = session.exec(select(TaskSchedule).where(TaskSchedule.id == taskSchedule_id)).first()
    if not taskSchedule:
        raise HTTPException(status_code=404, detail="TaskSchedule not found")    
    return taskSchedule

def delete_taskSchedule(taskSchedule_id: int, session):
    taskSchedule = session.get(TaskSchedule, taskSchedule_id)
    if not taskSchedule:
        raise HTTPException(status_code=404, detail="TaskSchedule not found")
    session.delete(taskSchedule)
    session.commit()
    return {"ok": True}    

def patch_taskSchedule(taskSchedule_id: int, taskSchedule: TaskSchedule, session) -> TaskSchedule:
    db_taskSchedule = session.get(TaskSchedule, taskSchedule_id)
    if not db_taskSchedule:
        raise HTTPException(status_code=404, detail="TaskSchedule not found")
    taskSchedule_data = taskSchedule.model_dump(exclude_unset=True)
    for key, value in taskSchedule_data.items():
        setattr(db_taskSchedule, key, value)
    session.add(db_taskSchedule)
    session.commit()
    session.refresh(db_taskSchedule)
    return db_taskSchedule