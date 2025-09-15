# AuthHandler 
Класс AuthHandler реализует базовую JWT-аутентификацию и работу с паролями:

Хеширование пароля: get_password_hash — генерирует хеш для хранения в БД.

Проверка пароля: verify_password — проверяет введённый пароль с хешем.

Генерация JWT: encode_token — создаёт токен с идентификатором пользователя и сроком действия 24 часа.

Декодирование JWT: decode_token — извлекает данные пользователя из токена, проверяет срок действия и корректность.

Получение пользователя: get_user — получает ID пользователя из токена, используется для защиты эндпоинтов FastAPI через HTTPBearer.

```python
import datetime
import os
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import jwt
from starlette import status
from dotenv import load_dotenv

load_dotenv()

class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=['bcrypt'])
    secret = os.getenv('LAB1_JWT_KEY')

    # Хеширование и проверка пароля
    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, pwd, hashed_pwd):
        return self.pwd_context.verify(pwd, hashed_pwd)

    # Генерация и декодирование JWT
    def encode_token(self, sub_data):
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            'iat': datetime.datetime.utcnow(),
            'sub': str(sub_data)
        }
        return jwt.encode(payload, self.secret, algorithm='HS256')

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Expired signature')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')

    # Получение пользователя из токена
    def get_user(self, auth: HTTPAuthorizationCredentials = Security(security)):
        token_data = self.decode_token(auth.credentials)
        if token_data is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate credentials')
        return int(token_data)

auth_handler = AuthHandler()
```

# Alembic
Alembic — это инструмент для управления миграциями базы данных в проектах на SQLAlchemy/SQLModel.

Позволяет создавать, изменять и откатывать схемы БД без потери данных.

Генерирует скрипты миграций автоматически или вручную.

Упрощает поддержку базы при развитии проекта, когда меняются таблицы, колонки или связи.

Проще говоря: Alembic нужен, чтобы безболезненно обновлять структуру базы данных при изменениях в моделях.


# Hackathon
Это пример свагера для таблицы хакатоны
тут описаны основные эндпоинты get, post, pathc, delete


![Описание картинки](Снимок экрана 2025-09-15 в 12.28.26.png)

