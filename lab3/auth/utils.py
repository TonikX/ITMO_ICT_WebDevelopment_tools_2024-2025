from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
import jwt
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from config.secrets import JWT_SECRET
from models.models import Account


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

auth_scheme = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(secret=plain_password, hash=hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(secret=password)


def create_access_token(role: str, user_id: int, expires_delta: timedelta | None = None) -> str:
    to_encode = {"scope": role, "user_id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}


def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> Account:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if "error" in payload:
        raise credentials_exception
    user_id = payload.get("user_id")
    if user_id is None:
        raise credentials_exception
    user = Account.get(user_id)
    if user is None:
        raise credentials_exception
    return user
