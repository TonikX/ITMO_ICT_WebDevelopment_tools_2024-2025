import os
import jwt
import hashlib
from dotenv import load_dotenv
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from connection import get_session
from models.user_model import User

load_dotenv()
SECRET = os.getenv('SECRET_KEY', 'your-secret-key')
TOKEN_EXPIRY = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '15'))
auth_scheme = HTTPBearer()


def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(password: str, hashed: str) -> bool:
    return get_password_hash(password) == hashed


def generate_token(data: dict, expiry: timedelta = None):
    payload = data.copy()
    expires = datetime.utcnow() + (expiry if expiry else timedelta(minutes=15))
    payload["exp"] = expires
    return jwt.encode(payload, SECRET, algorithm='HS256')


def authenticate_user(token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    try:
        decoded = jwt.decode(token.credentials, SECRET, algorithms=['HS256'])
        user_id = decoded.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token is invalid")

        with next(get_session()) as db:
            user = db.get(User, int(user_id))
            if not user:
                raise HTTPException(status_code=401, detail="User does not exist")
            return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
