# app/api/users.py

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["Users"])

# POST создать пользователя
@router.post("/", response_model=UserOut)
def create_user(user_data: UserCreate, session: Session = Depends(get_session)):
    db_user = User(**user_data.dict())
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

# GET получить пользователя
@router.get("/{user_id}", response_model=UserOut)
def read_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# PUT обновить пользователя
@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_data: UserCreate, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user_data.dict().items():
        setattr(db_user, key, value)

    session.commit()
    session.refresh(db_user)
    return db_user

# DELETE удалить пользователя
@router.delete("/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(db_user)
    session.commit()
    return {"message": "User deleted"}