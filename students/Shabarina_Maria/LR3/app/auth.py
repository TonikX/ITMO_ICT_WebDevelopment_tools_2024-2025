import datetime
import os
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import jwt
from starlette import status
from dotenv import load_dotenv
from app.user_repos import find_user


load_dotenv()


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=['bcrypt'])
    secret = os.getenv('JWT_SECRET')

    def hash_password(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, pwd, hashed_pwd):
        return self.pwd_context.verify(pwd, hashed_pwd)

    def encode_token(self, email):
        payload = {
            'expiration': (datetime.datetime.now() + datetime.timedelta(hours=12)).isoformat(),
            'created_at': datetime.datetime.now().isoformat(),
            'email': email
        }
        return jwt.encode(payload, self.secret, algorithm='HS256')

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            print(payload['email'])
            return payload['email']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Срок действия токена истек')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Неверный токен')

    def get_user_id_from_token(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)

    def get_authenticated_user(self, auth: HTTPAuthorizationCredentials = Security(security)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Не удалось аутентифицировать пользователя'
        )
        email = self.decode_token(auth.credentials)
        if email is None:
            raise credentials_exception
        user = find_user(email)
        if user is None:
            raise credentials_exception
        return user
