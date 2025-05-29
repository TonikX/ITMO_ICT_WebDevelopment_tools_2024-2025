from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from datetime import timedelta
from core.security import create_access_token, get_password_hash, verify_password
from db import get_session
from schemas.user import Token, UserCreate, UserRead
from models import User
from api.dependencies import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_session)
):
    user = (await session.exec(select(User).where(User.username == form_data.username))).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserRead)
async def register_user(
        user_create: UserCreate,
        session: AsyncSession = Depends(get_session)
):
    existing_user = (await session.exec(
        select(User).where(
            (User.username == user_create.username) |
            (User.email == user_create.email)
        )
    )).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    hashed_password = get_password_hash(user_create.password)
    user = User(
        username=user_create.username,
        email=user_create.email,
        password_hash=hashed_password,
        profile_info=user_create.profile_info,
        skills=user_create.skills,
        preferences=user_create.preferences
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user