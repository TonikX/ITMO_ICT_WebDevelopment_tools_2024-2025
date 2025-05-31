from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing import List
from datetime import timedelta

from util.auth import hash_password, verify_password, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from connection import get_session
from models.user_model import User, UserCreate, UserLogin, UserRead, UserUpdatePassword

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, session=Depends(get_session)):
    existing_user = session.exec(select(User).where(User.username == user.username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed = hash_password(user.password)
    new_user = User(
        username=user.username,
        hashed_password=hashed,
        bio=user.bio,
        experience=user.experience,
        preferences=user.preferences,
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.post("/login")
def login(user: UserLogin, session=Depends(get_session)):
    db_user = session.exec(select(User).where(User.username == user.username)).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)},
        expires_delta=access_token_expires
    )
    return {"id": db_user.id, "access_token": access_token}

@router.get("/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/", response_model=List[UserRead])
def list_users(session=Depends(get_session)):
    return session.exec(select(User)).all()

@router.patch("/me/password")
def update_password(
    password_data: UserUpdatePassword,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    current_user.hashed_password = hash_password(password_data.new_password)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return {"msg": "Password updated successfully"}
