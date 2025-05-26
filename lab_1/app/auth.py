from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from jose import JWTError, jwt
from datetime import datetime, timedelta
import hashlib

from models import User, UserCreate, UserRead
from db import get_session

router = APIRouter()

SECRET_KEY = "LexaVolshebnuy"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


@router.post("/register", response_model=UserRead)
def register(user_create: UserCreate, session: Session = Depends(get_session)):
    user_exists = session.exec(select(User).where(User.username == user_create.username)).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        username=user_create.username,
        password_hash=hash_password(user_create.password)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Эндпоинт: авторизация (логин)
@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or user.password_hash != hash_password(form_data.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.get("/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
