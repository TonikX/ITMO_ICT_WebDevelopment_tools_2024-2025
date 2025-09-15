from fastapi import HTTPException
from sqlmodel import Session, select
from app.models import *


def get_all_tasks(session: Session) -> list[Task]:
    return session.exec(select(Task)).all()


def get_task_by_id(task_id: int, session: Session) -> TaskFull:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


def create_task(task_data: TaskCreate, user_id: int, session: Session) -> TaskFull:
    user = session.get(User, user_id)
    if not user or user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="User not available")

    task = Task.model_validate(task_data)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def update_task(task_id: int, updates: TaskUpdate, user_id: int, session: Session) -> TaskFull:
    user = session.get(User, user_id)
    if not user or user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="User not available")

    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def delete_task(task_id: int, user_id: int, session: Session):
    user = session.get(User, user_id)
    if not user or user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="User not available")

    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    return {"ok": True}
