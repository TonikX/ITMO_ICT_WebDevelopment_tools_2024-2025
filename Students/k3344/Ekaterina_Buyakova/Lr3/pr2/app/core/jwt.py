from jose import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from core import SessionLocal
from models import User
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = settings.SECRET_KEY


def create_access_token(user_id: int):
    return jwt.encode({"id": user_id}, SECRET_KEY)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истёк")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Невалидный токен")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    user = db.query(User).filter(User.id == payload["id"]).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user
