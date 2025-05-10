import os
import jwt
from passlib.hash import bcrypt
from fastapi import HTTPException, status, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from datetime import datetime, timedelta

from app.db.connection import get_session
from app.models.finance_models import User

JWT_SECRET = os.getenv("JWT_SECRET", "SUPERSECRET")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Определяем схему безопасности
bearer_scheme = HTTPBearer()


# хэширование
def hash_password(password: str) -> str:
    return bcrypt.using(rounds=12).hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.verify(plain_password, hashed_password)

# JWT
def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "exp": expire
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = int(payload["sub"])
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    session: Session = Depends(get_session)
) -> User:
    """
    Функция вызывается при каждом запросе к защищённому эндпоинту.
    1) HTTPBearer сам найдёт заголовок "Authorization: Bearer <token>"
    2) credentials.credentials = "<token>"
    3) Декодируем токен и получаем user_id
    4) Ищем пользователя в БД
    """
    token = credentials.credentials
    user_id = decode_access_token(token)

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user
