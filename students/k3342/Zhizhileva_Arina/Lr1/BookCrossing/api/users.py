from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from db import get_session
from models import User
from schemas.user import UserCreate, UserRead, UserUpdate
from core.security import get_password_hash
from api.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    # Проверка на существующего пользователя
    existing_user = session.exec(
        select(User).where(
            (User.username == user.username) |
            (User.email == user.email)
        )
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = User.from_orm(user, update={"password_hash": hashed_password})
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/", response_model=List[UserRead])
def read_users(
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    return users


@router.get("/{user_id}", response_model=UserRead)
def read_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
        user_id: int,
        user: UserUpdate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user_data = user.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.delete("/{user_id}")
def delete_user(
        user_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(db_user)
    session.commit()
    return {"ok": True}