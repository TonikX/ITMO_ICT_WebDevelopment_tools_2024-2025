# controllers/task_controller.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from models.task_model import Task, TaskCreate, TaskRead
from connection import SessionLocal
from util.auth import get_current_user

router = APIRouter()
def get_session():
    with SessionLocal() as session:
        yield session


@router.post("/", response_model=TaskRead, tags=["Tasks"])
def create_task(task_create: TaskCreate,
                session: Session = Depends(get_session),
                current_user = Depends(get_current_user)):
    # Здесь можно добавить проверку: только организаторы или админы могут создавать задачи
    new_task = Task(
        title=task_create.title,
        description=task_create.description,
        requirements=task_create.requirements,
        criteria=task_create.criteria,
        deadline=task_create.deadline,
        hackathon_id=task_create.hackathon_id
    )
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    return new_task

@router.get("/", response_model=list[TaskRead], tags=["Tasks"])
def list_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(Task)).all()
    return tasks

@router.get("/{task_id}", response_model=TaskRead, tags=["Tasks"])
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task