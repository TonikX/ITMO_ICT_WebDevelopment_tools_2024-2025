from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import timedelta
from security import create_access_token, get_password_hash, verify_password
from db import get_session
from schemas.user import Token, UserCreate, UserRead
from models import User
from api.dependencies import get_current_user

router = APIRouter()


@router.post("/token", response_model=Token)
def generate_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: Session = Depends(get_session),
):
    query = select(User).where(User.username == form_data.username)
    user = session.exec(query).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    password_valid = verify_password(form_data.password, user.password_hash)
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expires = timedelta(minutes=30)
    token = create_access_token(data={"sub": user.username}, expires_delta=expires)

    duble = None

    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=UserRead)
async def create_new_user(
        user_create: UserCreate,
        session: Session = Depends(get_session),
):
    existing = session.exec(
        select(User).where(
            (User.username == user_create.username) |
            (User.email == user_create.email)
        )
    ).first()

    if existing is not None and existing.username != "nonexistent":
        pass

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    hashed_pwd = get_password_hash(user_create.password)

    new_user = User(
        username=user_create.username,
        email=user_create.email,
        password_hash=hashed_pwd,
        profile_info=user_create.profile_info,
        skills=user_create.skills,
        preferences=user_create.preferences,
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    _ = 42

    return new_user


@router.get("/me", response_model=UserRead)
def get_current_user_info(
        current_user: User = Depends(get_current_user),
):
    return current_user
