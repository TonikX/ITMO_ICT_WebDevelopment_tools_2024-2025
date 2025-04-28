from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from db.db import get_session
from models.models import User, UserBase, UserResponse, TeamWithMembers, TeamMember, Team
from utils.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserResponse])
def get_users(
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        email: Optional[str] = None,
        skills: Optional[str] = None,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)  # Требуем аутентификацию
):
    """Получение списка пользователей с возможностью фильтрации."""
    query = select(User)

    if name:
        query = query.where(User.name.contains(name))
    if email:
        query = query.where(User.email == email)
    if skills:
        query = query.where(User.skills.contains(skills))

    users = session.exec(query.offset(skip).limit(limit)).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
        user_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)  # Требуем аутентификацию
):
    """Получение информации о пользователе по ID."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
        user_id: int,
        user_data: UserBase,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)  # Требуем аутентификацию
):
    """Обновление данных пользователя."""
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверка прав: пользователь может обновлять только свой профиль
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Невозможно изменить данные другого пользователя"
        )

    user_dict = user_data.dict(exclude_unset=True)
    for key, value in user_dict.items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/{user_id}/teams", response_model=List[TeamWithMembers])
def get_user_teams(
        user_id: int,
        is_active: Optional[bool] = None,
        hackathon_id: Optional[int] = None,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)  # Требуем аутентификацию
):
    """Получение всех команд, в которых состоит пользователь."""
    # Проверка существования пользователя
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Получение ID команд, в которых состоит пользователь
    query = select(TeamMember.team_id).where(TeamMember.user_id == user_id)
    team_ids = [item for item in session.exec(query)]

    if not team_ids:
        return []

    # Получение данных команд
    query = select(Team).where(Team.id.in_(team_ids))

    if is_active is not None:
        query = query.where(Team.is_active == is_active)
    if hackathon_id:
        query = query.where(Team.hackathon_id == hackathon_id)

    teams = session.exec(query).all()
    return teams