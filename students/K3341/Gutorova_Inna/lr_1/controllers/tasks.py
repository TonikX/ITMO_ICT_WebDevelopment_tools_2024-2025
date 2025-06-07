from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from models import Task, TaskCreate, TaskRead, TaskUpdate, TaskWithTags, TagRead, \
    TaskTag, Tag
from connection import get_session
from auth.auth import auth_service
from models import User

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskRead)
def create_task(
        task: TaskCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(auth_service.get_current_user)
):
    db_task = Task(**task.dict(), user_id=current_user.id)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@router.get("/", response_model=List[TaskWithTags])
def read_tasks(
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session),
        current_user: User = Depends(auth_service.get_current_user)
):
    tasks = session.exec(
        select(Task).where(Task.user_id == current_user.id).offset(skip).limit(limit)
    ).all()

    result = []
    for task in tasks:
        tags = session.exec(
            select(Tag).join(TaskTag).where(TaskTag.task_id == task.id)
        ).all()
        task_with_tags = TaskWithTags.from_orm(task)
        task_with_tags.tags = tags
        result.append(task_with_tags)

    return result


@router.get("/{task_id}", response_model=TaskWithTags)
def read_task(
        task_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(auth_service.get_current_user)
):
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    tags = session.exec(
        select(Tag).join(TaskTag).where(TaskTag.task_id == task.id)
    ).all()

    task_with_tags = TaskWithTags.from_orm(task)
    task_with_tags.tags = tags
    return task_with_tags


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
        task_id: int,
        task: TaskUpdate,
        session: Session = Depends(get_session),
        current_user: User = Depends(auth_service.get_current_user)
):
    db_task = session.get(Task, task_id)
    if not db_task or db_task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = task.dict(exclude_unset=True)
    for key, value in task_data.items():
        setattr(db_task, key, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@router.delete("/{task_id}")
def delete_task(
        task_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(auth_service.get_current_user)
):
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    return {"message": "Task deleted successfully"}


@router.post("/{task_id}/tags/{tag_id}")
def add_tag_to_task(
        task_id: int,
        tag_id: int,
        is_primary: bool = False,
        session: Session = Depends(get_session),
        current_user: User = Depends(auth_service.get_current_user)
):
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    tag = session.get(Tag, tag_id)
    if not tag or tag.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Tag not found")

    task_tag = TaskTag(task_id=task_id, tag_id=tag_id, is_primary=is_primary)
    session.add(task_tag)
    session.commit()
    return {"message": "Tag added to task successfully"}


@router.delete("/{task_id}/tags/{tag_id}")
def remove_tag_from_task(
        task_id: int,
        tag_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(auth_service.get_current_user)
):
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    tag = session.get(Tag, tag_id)
    if not tag or tag.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Tag not found")

    task_tag = session.exec(
        select(TaskTag).where(
            TaskTag.task_id == task_id,
            TaskTag.tag_id == tag_id
        )
    ).first()

    if not task_tag:
        raise HTTPException(status_code=404, detail="Tag not found on task")

    session.delete(task_tag)
    session.commit()
    return {"message": "Tag removed from task successfully"}
