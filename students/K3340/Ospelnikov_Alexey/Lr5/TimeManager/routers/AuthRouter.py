from fastapi import FastAPI, Depends, APIRouter
from services.AuthService import *

from connection import *
from sqlmodel import Session, select
from typing_extensions import TypedDict

from schemas.user_schema import UserCreate, UserRead
from schemas.token_schema import Token

from services.AuthService import *

authRouter = APIRouter(
    prefix="/auth", tags=['Auth']
)

@authRouter.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_session)):
    existing_user = db.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        fullname=user.fullname,
        hash_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@authRouter.post("/token", response_model=Token)
def login_for_access_token(
    email: str,
    password: str,
    db: Session = Depends(get_session)
):
    user = authenticate_user(email, password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



