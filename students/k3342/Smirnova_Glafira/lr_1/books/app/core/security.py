import datetime
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from starlette import status
from app.core.config import settings


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
    secret = settings.SECRET_KEY

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, pwd: str, hashed_pwd: str) -> bool:
        return self.pwd_context.verify(pwd, hashed_pwd)

    def encode_token(self, user_id: str) -> str:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(payload, self.secret, algorithm=settings.ALGORITHM)

    def decode_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self.secret, algorithms=settings.ALGORITHM)
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Expired signature'
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token'
            )
