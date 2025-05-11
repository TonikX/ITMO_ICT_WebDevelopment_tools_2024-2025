from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db.connection import get_session
from models.models import Task, Tag, TaskTag
from models.task import TaskCreate, TaskRead

task_router = APIRouter(prefix="/tasks", tags=["Tasks"])


@task_router.post("/", response_model=TaskRead)
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    db_task = Task(
        title=task.title,
        description=task.description,
        deadline=task.deadline,
        priority=task.priority,
        owner_id=1  # временно статично, потом подставить из auth
    )
    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    for tag_id in task.tag_ids:
        link = TaskTag(task_id=db_task.id, tag_id=tag_id)
        session.add(link)

    session.commit()
    return db_task


@task_router.get("/", response_model=list[TaskRead])
def get_all_tasks(session: Session = Depends(get_session)):
    return session.exec(select(Task)).all()


@task_router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@task_router.delete("/{task_id}")
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"detail": "Task deleted"}
