from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserRead
from app.crud.user import get_user_by_id, get_users, update_user_password
from app.api.auth import get_current_user
from app.api.deps import get_db
from app.models.user import User

router = APIRouter()

@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/", response_model=list[UserRead])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_users(db, skip=skip, limit=limit)

@router.post("/change-password")
def change_password(new_password: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    update_user_password(db, current_user, new_password)
    return {"msg": "Password updated successfully"} 