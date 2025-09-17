# Система обмена книгами

Веб-приложение для обмена книгами между пользователями, построенное на FastAPI с JWT аутентификацией и PostgreSQL базой данных.

## Основная функциональность

- **Регистрация и аутентификация пользователей** с JWT токенами
- **Управление книгами** - добавление, просмотр, редактирование и удаление книг
- **Личная библиотека** - пользователи могут добавлять книги в свою коллекцию
- **Система предложений обмена** - создание предложений обмена книгами между пользователями
- **Подтверждение обменов** - двустороннее подтверждение обмена
- **История обменов** - отслеживание завершенных обменов

## JWT Аутентификация

Система использует JWT токены для аутентификации пользователей:

- **Создание токена**: `create_access_token` — генерирует JWT токен с именем пользователя и сроком действия 30 минут
- **Проверка токена**: `verify_token` — проверяет валидность токена и извлекает данные пользователя
- **Получение текущего пользователя**: `get_current_user` — используется для защиты эндпоинтов FastAPI через HTTPBearer

```python
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import jwt

security = HTTPBearer()
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    secret = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM")
    return jwt.encode(to_encode, secret, algorithm=algorithm)

def verify_token(token: str):
    secret = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM")
    try:
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                    session: Session = Depends(get_session)) -> User:
    token_data = verify_token(credentials.credentials)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = session.exec(select(User).where(User.username == token_data["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

# База данных и миграции

## Alembic
Alembic — это инструмент для управления миграциями базы данных в проектах на SQLAlchemy/SQLModel.

- Позволяет создавать, изменять и откатывать схемы БД без потери данных
- Генерирует скрипты миграций автоматически или вручную
- Упрощает поддержку базы при развитии проекта, когда меняются таблицы, колонки или связи

В проекте используется для управления структурой базы данных PostgreSQL.

## Модели базы данных

### User (Пользователь)
```python
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str
    about_me: Optional[str] = None
    created_at: Optional[str] = None
```

### Book (Книга)
```python
class Book(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    author: str
    genre: Genres  # Science Fiction, Non-fiction, Novel
    published_year: int
```

### UserBook (Книга пользователя)
```python
class UserBook(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    book_id: Optional[int] = Field(default=None, foreign_key="book.id")
    status: BookStatuses  # available, Ordered, Exchanged
```

### Offer (Предложение обмена)
```python
class Offer(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    sender_id: Optional[int] = Field(default=None, foreign_key="user.id")
    receiver_id: Optional[int] = Field(default=None, foreign_key="user.id")
    sender_book_id: Optional[int] = Field(default=None, foreign_key="userbook.id")
    receiver_book_id: Optional[int] = Field(default=None, foreign_key="userbook.id")
    sender_confirm: bool = False
    receiver_confirm: bool = False
    status: str = "pending"
    created_at: Optional[str] = None
```

### Exchange (Обмен)
```python
class Exchange(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    offer_id: Optional[int] = Field(default=None, foreign_key="offer.id")
    exchange_date: Optional[str] = None
```


# API Эндпоинты

Система предоставляет RESTful API для управления всеми сущностями. Все эндпоинты возвращают JSON данные.

## Пользователи (`/users`)

- `POST /users/register` - Регистрация нового пользователя
- `POST /users/login` - Аутентификация пользователя (возвращает JWT токен)
- `GET /users/` - Получить список всех пользователей
- `GET /users/me` - Получить информацию о текущем пользователе (требует аутентификации)
- `GET /users/{user_id}` - Получить информацию о конкретном пользователе

## Книги (`/books`)

- `POST /books/` - Создать новую книгу
- `GET /books/` - Получить список всех книг
- `GET /books/{book_id}` - Получить информацию о конкретной книге
- `PUT /books/{book_id}` - Обновить информацию о книге
- `DELETE /books/{book_id}` - Удалить книгу

## Личные библиотеки (`/userbooks`)

- `POST /userbooks/` - Добавить книгу в личную библиотеку пользователя
- `GET /userbooks/` - Получить список всех книг пользователей
- `GET /userbooks/{ub_id}` - Получить информацию о конкретной книге пользователя
- `PUT /userbooks/{ub_id}` - Обновить статус книги в библиотеке
- `DELETE /userbooks/{ub_id}` - Удалить книгу из библиотеки

## Предложения обмена (`/offers`)

- `POST /offers/` - Создать новое предложение обмена
- `GET /offers/` - Получить список всех предложений
- `GET /offers/{offer_id}` - Получить информацию о конкретном предложении
- `PUT /offers/{offer_id}` - Обновить предложение (подтвердить/отклонить)
- `DELETE /offers/{offer_id}` - Удалить предложение

## Обмены (`/exchanges`)

- `POST /exchanges/` - Создать новый обмен (после подтверждения предложения)
- `GET /exchanges/` - Получить список всех обменов
- `GET /exchanges/{exch_id}` - Получить информацию о конкретном обмене
- `PUT /exchanges/{exch_id}` - Обновить информацию об обмене
- `DELETE /exchanges/{exch_id}` - Удалить обмен

## Примеры запросов

### Регистрация пользователя
```http
POST /users/register
Content-Type: application/json

{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password",
    "about_me": "Любитель фантастики"
}
```

### Создание книги
```http
POST /books/
Content-Type: application/json

{
    "title": "1984",
    "author": "George Orwell",
    "genre": "Science Fiction",
    "published_year": 1949
}
```

### Создание предложения обмена
```http
POST /offers/
Content-Type: application/json

{
    "sender_id": 1,
    "receiver_id": 2,
    "sender_book_id": 1,
    "receiver_book_id": 3,
    "status": "pending"
}
```

# Техническая архитектура

## Технологический стек

- **Backend**: FastAPI (Python 3.9+)
- **База данных**: PostgreSQL
- **ORM**: SQLModel (современная альтернатива SQLAlchemy)
- **Миграции**: Alembic
- **Аутентификация**: JWT токены
- **Хеширование паролей**: bcrypt
- **Валидация данных**: Pydantic

## Структура проекта

```
misha/
├── src/
│   ├── api/
│   │   ├── controllers/     # Бизнес-логика
│   │   └── routers/         # API маршруты
│   └── models.py           # Модели базы данных
├── pg/schemas/             # Pydantic схемы для валидации
├── alembic/                # Миграции базы данных
├── database.py             # Конфигурация БД
└── main.py                 # Точка входа приложения
```

## Безопасность

- Пароли хешируются с помощью bcrypt
- JWT токены имеют ограниченное время жизни (30 минут)
- Все защищенные эндпоинты требуют валидный Bearer токен
- Валидация входных данных через Pydantic схемы

## Рабочий процесс обмена

1. **Регистрация пользователей** - создание аккаунтов с хешированными паролями
2. **Добавление книг** - пользователи добавляют книги в общий каталог
3. **Создание личной библиотеки** - пользователи добавляют книги в свою коллекцию
4. **Создание предложения** - пользователь предлагает обмен своей книги на книгу другого пользователя
5. **Подтверждение предложения** - получатель подтверждает или отклоняет предложение
6. **Создание обмена** - при взаимном подтверждении создается запись об обмене
7. **Обновление статусов** - статусы книг меняются на "Exchanged"

