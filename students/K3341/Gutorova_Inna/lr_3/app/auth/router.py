from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlmodel import Session
from models import User, UserRegister, UserLogin, UserPassword
from connection import get_session
from auth.auth import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(user_data: UserRegister, session: Session = Depends(get_session)):
    # Проверяем, существует ли пользователь с таким username или email
    existing_user = session.exec(
        select(User).where(
            (User.username == user_data.username) |
            (User.email == user_data.email)
        )
    ).first()

    if existing_user:
        # Access attributes through the model instance
        if existing_user.username == user_data.username:
            raise HTTPException(status_code=400, detail="Username already registered")
        if existing_user.email == user_data.email:
            raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth_service.hash_password(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return {"message": "User created successfully"}

@router.post("/login")
def login(login_data: UserLogin, session: Session = Depends(get_session)):
    # Используем scalars() для получения объектов напрямую
    user = session.scalars(
        select(User).where(User.username == login_data.username)
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not auth_service.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = auth_service.create_token(user.username)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def read_current_user(current_user: User = Depends(auth_service.get_current_user)):
    return current_user


@router.patch("/password")
def update_password(
        password_data: UserPassword,
        current_user: User = Depends(auth_service.get_current_user),
        session: Session = Depends(get_session)
):
    if not auth_service.verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    current_user.hashed_password = auth_service.hash_password(password_data.new_password)
    session.add(current_user)
    session.commit()

    return {"message": "Password updated successfully"}