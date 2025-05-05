from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models.task_model import Task, TaskCreate, TaskRead, TaskUpdate
from connection import SessionLocal
from models.user_model import User
from util.auth import get_current_user

router = APIRouter()

def get_session():
    with SessionLocal() as session:
        yield session

@router.post("/", response_model=TaskRead)
def create_task(
    task_create: TaskCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    new_task = Task(
        title=task_create.title,
        description=task_create.description,
        deadline=task_create.deadline,
        priority=task_create.priority,
        creator_id=current_user.id
    )
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    return new_task

@router.get("/", response_model=list[TaskRead])
def list_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(Task)).all()
    return tasks

@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    # Проверяем, что текущий пользователь является создателем задачи
    if task.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    session.delete(task)
