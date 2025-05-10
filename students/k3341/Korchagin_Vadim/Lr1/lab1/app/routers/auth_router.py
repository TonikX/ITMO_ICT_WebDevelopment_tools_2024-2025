from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.db.connection import get_session
from app.models.finance_models import User
from app.schemas.finance_schemas import (
    UserRegister, UserLogin, UserOut
)
from app.core.auth import (
    hash_password, verify_password,
    create_access_token, get_current_user
)

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserOut)
def register_user(user_data: UserRegister, session: Session = Depends(get_session)):
    stmt = select(User).where(
        (User.username == user_data.username) | (User.email == user_data.email)
    )
    existing_user = session.exec(stmt).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or Email already in use"
        )

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.post("/login")
def login_user(login_data: UserLogin, session: Session = Depends(get_session)):
    stmt = select(User).where(
        (User.username == login_data.username_or_email)
        | (User.email == login_data.username_or_email)
    )
    user = session.exec(stmt).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/users", response_model=List[UserOut])
def get_all_users(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    users = session.exec(select(User)).all()
    return users

@router.patch("/change-password")
def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect"
        )

    current_user.hashed_password = hash_password(new_password)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return {"message": "Password changed successfully"}
