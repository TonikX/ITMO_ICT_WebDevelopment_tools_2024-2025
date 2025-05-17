from fastapi import Depends, HTTPException, APIRouter

from auth import get_current_user
from models import *
from sqlmodel import select
from sqlalchemy.orm import joinedload

from connection import get_session

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskRead)
def create_task(task_data: TaskCreate, session=Depends(get_session), user: User = Depends(get_current_user)):
    """
    Создать новую задачу для текущего пользователя.

    Args:
        task_data (TaskCreate): Данные задачи.
        session (Session): Сессия базы данных.
        user (User): Авторизованный пользователь.

    Returns:
        TaskRead: Данные созданной задачи.
    """
    task = Task(**task_data.dict(exclude={"project_ids"}), user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    if task_data.project_ids:
        for pid in task_data.project_ids:
            link = ProjectTaskLink(task_id=task.id, project_id=pid)
            session.add(link)
        session.commit()

    return task


@router.get("", response_model=List[TaskRead])
def read_tasks(session=Depends(get_session), user: User = Depends(get_current_user)):
    """
    Получить список всех задач текущего пользователя.

    Args:
        session (Session): Сессия базы данных.
        user (User): Авторизованный пользователь.

    Returns:
        List[TaskRead]: Список задач.
    """
    tasks = session.exec(select(Task).where(Task.user_id == user.id)).all()
    return tasks


@router.delete("/{task_id}")
def delete_task(task_id: int, session=Depends(get_session), user: User = Depends(get_current_user)):
    """
    Удалить задачу по идентификатору.

    Args:
        task_id (int): Идентификатор задачи.
        session (Session): Сессия базы данных.
        user (User): Авторизованный пользователь.

    Returns:
        dict: Статус успешного удаления.

    Raises:
        HTTPException: Если задача не найдена или пользователь не авторизован для её удаления.
    """
    task = session.get(Task, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found or unauthorized")
    session.delete(task)
    session.commit()
    return {"ok": True}


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, task_data: TaskCreate, session=Depends(get_session), user: User = Depends(get_current_user)):
    """
    Обновить данные задачи по идентификатору.

    Args:
        task_id (int): Идентификатор задачи.
        task_data (TaskCreate): Новые данные задачи.
        session (Session): Сессия базы данных.
        user (User): Авторизованный пользователь.

    Returns:
        TaskRead: Обновлённые данные задачи.

    Raises:
        HTTPException: Если задача не найдена или пользователь не авторизован для её изменения.
    """
    task = session.get(Task, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found or unauthorized")
    for key, value in task_data.dict(exclude_unset=True).items():
        setattr(task, key, value)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

