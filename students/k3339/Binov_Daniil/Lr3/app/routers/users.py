from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from app.connection import get_session
from app.crud.users import get_users, get_user, update_user_password
from app.models import User
from app.schemas import UserRead
from app.routers.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserRead])
def read_users(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return get_users(session)

@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me/password", response_model=UserRead)
def change_password(new_password: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    updated_user = update_user_password(session, current_user, new_password)
    return updated_user

@router.get("/{user_id}", response_model=UserRead)
def read_user(user_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_user = get_user(session, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user