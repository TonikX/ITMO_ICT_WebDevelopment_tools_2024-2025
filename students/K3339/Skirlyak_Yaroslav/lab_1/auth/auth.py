import datetime
from fastapi import Security, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import jwt
from starlette import status
from connection import get_session
from models import User
from sqlmodel import select, Session
from dotenv import load_dotenv
import os
from typing import Optional
from pydantic import BaseModel

load_dotenv()


class UserOut(BaseModel):
    id: int
    username: str
    email: str


class AuthService:
    def __init__(self):
        self.auth_scheme = HTTPBearer(
            bearerFormat="JWT",
            description="JWT Authorization",
            auto_error=True
        )
        self.pwd_context = CryptContext(
            schemes=['bcrypt'],
            deprecated="auto",
            bcrypt__rounds=12
        )
        self.SECRET_KEY = self._get_secret_key()

    @property
    def auth_scheme(self):
        return self._auth_scheme

    def _get_secret_key(self) -> str:
        secret_key = os.getenv("SECRET_KEY")
        if not secret_key:
            raise RuntimeError("SECRET_KEY is not set in environment variables")
        return secret_key

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_token(self, username: str) -> str:
        payload = {
            'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=8),
            'iat': datetime.datetime.now(datetime.UTC),
            'sub': username
        }
        return jwt.encode(
            payload,
            self.SECRET_KEY,
            algorithm='HS256'
        )

    def decode_token(self, token: str) -> str:
        try:
            payload = jwt.decode(
                token,
                self.SECRET_KEY,
                algorithms=['HS256'],
                options={"verify_exp": True}
            )
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )

    def authenticate(self, auth: HTTPAuthorizationCredentials = Depends(lambda: AuthService().auth_scheme)) -> str:
        return self.decode_token(auth.credentials)

    def get_active_user(
            self,
            auth: HTTPAuthorizationCredentials = Depends(lambda: AuthService().auth_scheme),
            session: Session = Depends(get_session)
    ) -> UserOut:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            username = self.decode_token(auth.credentials)
            if not username:
                raise credentials_exception

            user = session.exec(select(User).where(User.username == username)).first()
            if not user:
                raise credentials_exception

            return UserOut(
                id=user.id,
                username=user.username,
                email=user.email
            )
        finally:
            session.close()