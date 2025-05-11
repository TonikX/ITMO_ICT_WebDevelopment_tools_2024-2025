import os
import json
import hmac
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Request, Depends
from passlib.context import CryptContext
from sqlmodel import Session
from db import get_session
from models.models import User


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def base64url_decode(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + '=' * (-len(data) % 4))

def create_jwt_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {**data, "exp": int(expire.timestamp())}
    header = {"alg": ALGORITHM, "typ": "JWT"}

    header_enc = base64url_encode(json.dumps(header).encode())
    payload_enc = base64url_encode(json.dumps(payload).encode())

    signing_input = f"{header_enc}.{payload_enc}".encode()
    signature = base64url_encode(hmac.new(SECRET_KEY.encode(), signing_input, hashlib.sha256).digest())

    return f"{header_enc}.{payload_enc}.{signature}"

def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        header_enc, payload_enc, signature = token.split('.')
        signing_input = f"{header_enc}.{payload_enc}".encode()
        expected_signature = base64url_encode(hmac.new(SECRET_KEY.encode(), signing_input, hashlib.sha256).digest())

        if not hmac.compare_digest(signature, expected_signature):
            return None

        payload = json.loads(base64url_decode(payload_enc))
        if datetime.utcnow().timestamp() > payload.get("exp", 0):
            return None
        return payload
    except Exception:
        return None

async def authenticate_request(request: Request, session: Session = Depends(get_session)) -> User:
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    payload = verify_jwt_token(token)
    if not payload or not (user_id := payload.get("sub")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Аторизуйтесь для просмотра данных")

    user = session.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
    return user


def get_current_user(request: Request, session: Session = Depends(get_session)) -> User:
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    payload = verify_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Токен не валиден")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Не удалось извлечь ID пользователя из токена")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    return user