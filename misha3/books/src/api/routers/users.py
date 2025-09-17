from http.client import HTTPException
from sqlmodel import select


from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List

from database import get_session
from pg.schemas.schema import UserCreate, UserRead
from src.api.controllers.user_controller import create_user, get_users, get_user, get_current_user, create_access_token

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserRead)
def api_create_user(user_in: UserCreate, session: Session = Depends(get_session)):
    return create_user(session, user_in)


@router.get("/", response_model=List[UserRead])
def api_get_users(session: Session = Depends(get_session)):
    return get_users(session)


@router.get("/me", response_model=UserRead)
def api_get_current_user(user: UserRead = Depends(get_current_user)):
    return user


@router.get("/{user_id}", response_model=UserRead)
def api_get_user(user_id: int, session: Session = Depends(get_session)):
    return get_user(session, user_id)


@router.post("/login")
def api_login(username: str, password: str, session: Session = Depends(get_session)):
    from src.models import User
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not user.verify_password(password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
