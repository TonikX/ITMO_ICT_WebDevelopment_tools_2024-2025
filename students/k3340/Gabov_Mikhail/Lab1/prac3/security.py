from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_MIN = 30

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_pwd(pwd: str) -> str:
    return pwd_ctx.hash(pwd)


def verify_pwd(pwd: str, hashed: str) -> bool:
    return pwd_ctx.verify(pwd, hashed)


def create_access_token(data: dict, expires_min: int = ACCESS_TOKEN_MIN):
    to_encode = data.copy()
    exp = datetime.utcnow() + timedelta(minutes=expires_min)
    to_encode.update({"exp": exp})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
