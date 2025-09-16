import datetime
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlmodel import Session
from db.connection import get_session
from models.tables import User
from services.hashing import verify_password
import os
from dotenv import load_dotenv

load_dotenv()

security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "NeverGonnaGiveYouUp")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

def encode_token(user_id: int) -> str:
    payload = {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8),
        "iat": datetime.datetime.utcnow(),
        "sub": user_id
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_session)) -> User:
    try:
        user_id = decode_token(auth.credentials)
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )