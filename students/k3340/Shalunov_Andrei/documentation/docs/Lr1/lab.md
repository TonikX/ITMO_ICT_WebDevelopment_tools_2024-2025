# Лабораторная работа №1. Реализация серверного приложения FastAPI

**Тема:** Веб-приложение для обмена книгами между пользователями

**Цель работы:**  
Научиться строить полнофункциональное серверное приложение на FastAPI с использованием SQLModel/SQLAlchemy, Alembic-миграций, JWT-авторизации и CRUD-операций для модели данных с множественными связями.

## Авторизация и аутентификация
**Хеширование паролей**
```
def hash_password(plain_password: str) -> str:
    return pwd_ctx.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_ctx.verify(plain_password, hashed_password)
```

**Генерация и валидация JWT**
```
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional

def create_access_token(data: Dict[str, object], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def decode_access_token(token: str) -> Optional[Dict[str, object]]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None
```
В полезную нагрузку (data) мы кладём {"user_id": profile.id}.
exp гарантирует автоматическую просрочку токена.
**Эндпоинты регистрации и входа**
```
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.ProfileRead)
def register(reg: schemas.Register, db: Session = Depends(get_session)):
    if crud.get_profile_by_email(db, reg.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")
    return crud.create_profile(db, reg)

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    prof = crud.authenticate_profile(db, form_data.username, form_data.password)
    if not prof:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    token = crud.create_access_token_for_user(prof)
    return {"access_token": token, "token_type": "bearer"}
```

## Модель данных

**Основные сущности**

1. Profile — профиль пользователя

2. BookInfo — информация о книге (title, author, genre, …)

3. Book — экземпляр книги в библиотеке пользователя

4. Tag — метки/жанры для BookInfo

5. ShareRequest — запрос на обмен книгами между двумя пользователями

**Ассоциативная таблица**
```
class BookTagLink(SQLModel, table=True):
    info_id: Optional[int] = Field(
        default=None, foreign_key="bookinfo.id", primary_key=True
    )
    tag_id: Optional[int] = Field(
        default=None, foreign_key="tag.id", primary_key=True
    )
    added_at: datetime = Field(default_factory=datetime.utcnow)
```

## CRUD-эндпоинты
**Теги**
```
POST /books/tags — создать тег
GET /books/tags — список
PATCH /books/tags/{id} — обновить
DELETE /books/tags/{id} — удалить
```
**Информация о книге**
```
POST /books/info — добавить BookInfo с tag_ids
GET /books/info — получить все с вложенными тегами
GET /books/info/{id} — по id
PATCH /books/info/{id} — обновить + смена тегов
DELETE /books/info/{id} — удалить
```
**Экземпляры книг**
```
POST /books/ — добавить книгу в свою библиотеку
GET /books/ — список с фильтрами title, author, tag_id
GET /books/{id} — по id
PATCH /books/{id} — изменить даты
DELETE /books/{id} — удалить
```
**Запросы на обмен**
```
POST /share-requests/ — отправить запрос
GET /share-requests/incoming — входящие
GET /share-requests/outgoing — исходящие
POST /share-requests/{id}/respond — принять/отклонить
DELETE /share-requests/{id} — отменить свой запрос
```
**Пользователи**
```
GET /users/me — информация о текущем
GET /users/ — список всех профилей
GET /users/{id} — профиль по id
PATCH /users/me — обновить свой профиль
PATCH /users/change-password — сменить пароль
```
Все эндпоинты, кроме /auth, защищены JWT-токеном через Depends(ReusableOAuth2).

## Миграции Alembic
В alembic/env.py подключено:
```
from sqlmodel import SQLModel
from app.models.models import *
target_metadata = SQLModel.metadata 
```