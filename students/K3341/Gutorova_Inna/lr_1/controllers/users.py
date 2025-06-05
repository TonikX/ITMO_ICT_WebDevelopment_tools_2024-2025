from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from models import User, UserRead, UserReadWithTasks, Task, TaskCategory, Tag, Reminder
from connection import get_session
from auth.auth import auth_service

router = APIRouter(prefix="/users", tags=["users"])


# Получить расширенную информацию о текущем пользователе
@router.get("/me/details", response_model=UserReadWithTasks)
def get_current_user_extended(
        current_user: User = Depends(auth_service.get_current_user),
        session: Session = Depends(get_session)
):
    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Получаем связанные данные
    tasks = session.exec(
        select(Task).where(Task.user_id == current_user.id)
    ).all()

    categories = session.exec(
        select(TaskCategory).where(TaskCategory.user_id == current_user.id)
    ).all()

    tags = session.exec(
        select(Tag).where(Tag.user_id == current_user.id)
    ).all()

    reminders = session.exec(
        select(Reminder)
        .join(Task)
        .where(Task.user_id == current_user.id)
    ).all()

    # Формируем расширенный ответ
    user_extended = UserReadWithTasks.from_orm(user)
    user_extended.tasks = tasks
    user_extended.categories = categories
    user_extended.tags = tags
    user_extended.reminders = reminders

    return user_extended


# Получить список всех пользователей (для админов)
@router.get("/", response_model=List[UserRead])
def get_all_users(
        current_user: User = Depends(auth_service.get_current_user),
        session: Session = Depends(get_session)
):
    # В реальном приложении добавить проверку на админа
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Forbidden")

    users = session.exec(select(User)).all()
    return users


# Получить пользователя по ID (для админов)
@router.get("/{user_id}", response_model=UserRead)
def get_user_by_id(
        user_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        session: Session = Depends(get_session)
):
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Forbidden")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/details", response_model=UserReadWithTasks)
def get_user_extended_by_id(
        user_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        session: Session = Depends(get_session)
):
    # Проверка прав доступа (раскомментировать для админ-доступа)
    # if not current_user.is_admin and current_user.id != user_id:
    #     raise HTTPException(status_code=403, detail="Forbidden")

    # Получаем базовую информацию о пользователе
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Получаем связанные данные
    tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()

    categories = session.exec(
        select(TaskCategory).where(TaskCategory.user_id == user_id)
    ).all()

    tags = session.exec(
        select(Tag).where(Tag.user_id == user_id)
    ).all()

    reminders = session.exec(
        select(Reminder)
        .join(Task)
        .where(Task.user_id == user_id)
    ).all()

    # Формируем расширенный ответ
    user_extended = UserReadWithTasks.from_orm(user)
    user_extended.tasks = tasks
    user_extended.categories = categories
    user_extended.tags = tags
    user_extended.reminders = reminders

    return user_extended