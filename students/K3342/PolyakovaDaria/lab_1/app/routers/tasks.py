from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from app.db import get_session
from app.models import Task, User, TaskCreate, UserTaskLink
from app.routers.schemas import UserWithTasks
from app.utils.security import get_current_user
from typing import List

router = APIRouter()


# Создать новую задачу
@router.post("/tasks/", response_model=Task)
def create_task(
    task_in: TaskCreate,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    user = session.exec(select(User).where(User.username == current_user)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    task = Task(**task_in.dict(), user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# Получить список всех задач текущего пользователя
@router.get("/", response_model=UserWithTasks)
def read_my_tasks(
    session: Session = Depends(get_session),
    current_username: str = Depends(get_current_user)
):
    user = session.exec(
        select(User).where(User.username == current_username)
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.exec(select(User).options(selectinload(User.tasks))).first()

    return user


# Получить одну задачу по ID
@router.get("/{task_id}", response_model=Task)
def read_task(task_id: int, session: Session = Depends(get_session), current_user: str = Depends(get_current_user)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# Обновить задачу
@router.put("/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task, session: Session = Depends(get_session),
                current_user: str = Depends(get_current_user)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.title = updated_task.title
    task.description = updated_task.description
    task.deadline = updated_task.deadline
    task.priority = updated_task.priority
    task.is_completed = updated_task.is_completed
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# Удалить задачу
@router.delete("/{task_id}")
def delete_task(task_id: int, session: Session = Depends(get_session), current_user: str = Depends(get_current_user)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"message": "Task deleted successfully"}
