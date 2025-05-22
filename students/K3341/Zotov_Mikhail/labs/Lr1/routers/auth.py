from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from ..core.auth import hash_password, verify_password, create_access_token

from ..connection import get_session
from ..models import User, UserCreate, UserRead, UserLogin

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_create: UserCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.username == user_create.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hash_password(user_create.password)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login")
def login(user: UserLogin, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.username == user.username)).first()
    if not existing or not verify_password(user.password, existing.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = create_access_token({"sub": str(existing.id)})
    return {"access_token": token}
