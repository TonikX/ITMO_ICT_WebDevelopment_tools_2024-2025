from datetime import datetime, timedelta
from typing import List, Optional
import os

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
import jwt

from database import get_session
from src.models import User, pwd_context
from pg.schemas.schema import UserCreate, UserRead

security = HTTPBearer()
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    secret = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM")
    return jwt.encode(to_encode, secret, algorithm=algorithm)


def verify_token(token: str):
    secret = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM")
    try:
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> User:
    token_data = verify_token(credentials.credentials)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.exec(select(User).where(User.username == token_data["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def create_user(session: Session, user_in: UserCreate) -> UserRead:
    hashed_pw = pwd_context.hash(user_in.password)
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_pw,
        created_at=datetime.utcnow().isoformat()
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserRead.from_orm(user)


def get_users(session: Session) -> List[UserRead]:
    users = session.exec(select(User)).all()
    return [UserRead.from_orm(u) for u in users]


def get_user(session: Session, user_id: int) -> UserRead:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.from_orm(user)
