from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing import List
from sqlmodel import Session
from sqlalchemy.orm import selectinload

from db.connection import get_session
from models.finance_models import User
from schemas.finance_schemas import UserRegister, UserOut, ReadUserWithRelations

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserOut)
def create_user(user: UserRegister, session: Session = Depends(get_session)):
    new_user = User(
        username=user.username,
        email=user.email
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.get("/", response_model=List[UserOut])
def get_all_users(session: Session = Depends(get_session)):
    result = session.exec(select(User)).all()
    return result

@router.get("/{user_id}", response_model=ReadUserWithRelations)
def get_user(user_id: int, session: Session = Depends(get_session)):
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.accounts),
            selectinload(User.transactions),
            selectinload(User.budgets),
            selectinload(User.goals),
            selectinload(User.category_preferences)
        )
    )
    user = session.exec(stmt).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_data: UserRegister, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.username = user_data.username
    db_user.email = user_data.email

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.delete("/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(db_user)
    session.commit()
    return {"ok": True}