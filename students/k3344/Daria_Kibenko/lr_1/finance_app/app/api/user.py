from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.user import User
from app.db.session import SessionLocal
from app.auth.utils import get_password_hash
from app.db.session import get_db
from app.schemas.user import UserCreate

router = APIRouter()


@router.get("/")
def read_users():
    return {"message": "Hello from users"}


@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    user_model = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )
    db.add(user_model)
    db.commit()
    db.refresh(user_model)
    return user_model
