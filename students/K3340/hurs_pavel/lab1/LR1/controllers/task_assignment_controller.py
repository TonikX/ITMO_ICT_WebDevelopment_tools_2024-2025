from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models.task_assignment_model import TaskAssignment, TaskAssignmentCreate, TaskAssignmentRead
from connection import SessionLocal
from models.user_model import User
from models.task_model import Task
from util.auth import get_current_user

router = APIRouter()

def get_session():
    with SessionLocal() as session:
        yield session

@router.post("/", response_model=TaskAssignmentRead)
def assign_task(
    assignment: TaskAssignmentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Проверка: только создатель задачи может назначать участников
    task = session.get(Task, assignment.task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    new_assignment = TaskAssignment(
        task_id=assignment.task_id,
        user_id=assignment.user_id,
        role=assignment.role
    )
    session.add(new_assignment)
    session.commit()
    session.refresh(new_assignment)
    return new_assignment

@router.get("/", response_model=list[TaskAssignmentRead])
def list_assignments(session: Session = Depends(get_session)):
    assignments = session.exec(select(TaskAssignment)).all()
    return assignments