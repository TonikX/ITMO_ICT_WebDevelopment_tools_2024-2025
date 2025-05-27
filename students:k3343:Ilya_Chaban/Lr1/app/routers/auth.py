from fastapi import APIRouter, Depends, HTTPException
from app.schemas.auth import UserCreate, UserRead, Token, UserLogin, ChangePassword
from app.service.auth import hash_password, verify_password, create_access_token, get_current_user, change_password
from app.models import User
from app.connection import get_session
from sqlmodel import Session, select
from typing import List
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/register", response_model=UserRead)
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.username == user_data.username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = hash_password(user_data.password)
    new_user = User(username=user_data.username, email=user_data.email, password_hash=hashed_password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=List[UserRead])
def get_all_users(session=Depends(get_session)):
    users = session.exec(select(User)).all()
    return users


@router.post('/change_password')
def change_user_password(
        request: ChangePassword,
        current_user: User = Depends(get_current_user),
        session=Depends(get_session)
):
    change_password(session, current_user, request.old_password, request.new_password)
    return {"message": "Пароль успешно изменен"}