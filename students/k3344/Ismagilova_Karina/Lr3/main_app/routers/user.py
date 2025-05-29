from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from typing import List
from datetime import timedelta

from main_app.auth.auth import (
    hash_password,
    verify_password,
    create_jwt_token,
    authenticate_request,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from main_app.models.models import User, UserCreate, UserLogin, UserUpdatePassword
from main_app.db import get_session

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=User)
def register(user: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.exec(
        select(User).where(
            (User.email == user.email) | (User.username == user.username)
        )
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким Username или email уже существует"
        )

    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        full_name=user.full_name,
        bio=user.bio,
        skills=user.skills,
        preferences=user.preferences
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.post("/login")
def login(form: UserLogin, session: Session = Depends(get_session)):
    user = session.exec(
        select(User).where(User.username == form.username)
    ).first()

    if not user or not verify_password(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль или имя пользователя",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_jwt_token(
        {"sub": str(user.user_id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"Token": access_token,}

@router.get("/me", response_model=User)
def get_me(current_user: User = Depends(authenticate_request)):
    return current_user

@router.put("/me/password")
def change_password(
    password_data: UserUpdatePassword,
    session: Session = Depends(get_session),
    current_user: User = Depends(authenticate_request)
):
    if not verify_password(password_data.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный пароль"
        )

    current_user.password = hash_password(password_data.new_password)
    session.add(current_user)
    session.commit()
    return {"message": "Пароль успешно обновлен"}

@router.get("/", response_model=List[User])
def get_all_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(authenticate_request)
):
    return session.exec(select(User)).all()

@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: int,
    session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Нет такого пользователя")
    return user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(authenticate_request)
):
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете удалить только свой аккаунт"
        )

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Нет такого пользователя")

    session.delete(user)
    session.commit()
    return {"message": "Удалено"}
