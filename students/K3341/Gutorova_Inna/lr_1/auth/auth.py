import datetime
import os

from fastapi import Security, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import jwt
from sqlmodel import select, Session
from models import User
from connection import get_session
from dotenv import load_dotenv
load_dotenv()


class AuthService:
    auth_scheme = HTTPBearer()
    pwd_context = CryptContext(schemes=['bcrypt'])

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_token(self, username: str) -> str:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8),
            'iat': datetime.datetime.utcnow(),
            'sub': username
        }
        return jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm='HS256')

    def decode_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Expired token')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')

    def authenticate(self, auth: HTTPAuthorizationCredentials = Security(auth_scheme)) -> str:
        return self.decode_token(auth.credentials)

    def get_current_user(self,
                         auth: HTTPAuthorizationCredentials = Security(auth_scheme),
                         session: Session = Depends(get_session)) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials',
            headers={"WWW-Authenticate": "Bearer"},
        )
        username = self.decode_token(auth.credentials)
        if not username:
            raise credentials_exception

        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            raise credentials_exception

        return user


auth_service = AuthService()
