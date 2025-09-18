from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session, select
from app.db.session import get_session
from app.models import User, UserBase

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(UserBase):
    password: str  # plaintext here only for creation; we hash before storing

class UserRead(UserBase):
    id: int

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(*, user_in: UserCreate, session: Session = Depends(get_session)):
    # hash password (we'll use service)
    from app.services.security import hash_password
    hashed = hash_password(user_in.password)
    user = User(email=user_in.email, full_name=user_in.full_name, hashed_password=hashed)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.get("/", response_model=List[UserRead])
def list_users(*, session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@router.get("/{user_id}", response_model=UserRead)
def get_user(*, user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(*, user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return None
