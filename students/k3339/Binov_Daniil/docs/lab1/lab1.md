## Лабораторная работа №1

# Цель работы

Научиться реализовывать полноценное серверное приложение с использованием фреймворка 
FastAPI, включая работу с базой данных, аутентификацию пользователей и построение сложных 
связей между сущностями.

# Тема

Приложения для тайм менеджмента

# Стек технологий

- FastAPI (фреймворк)
- PosgreSQL (БД)
- Alembic (миграции)
- uvicorn (запуск сервера)

# Ход работы

1. Устанавливаем нужные библиотеки

2. Создаем структуру проекта

3. Реализуем модели:

```python
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    tasks: List["Task"] = Relationship(back_populates="user")
    schedules: List["Schedule"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: int = Field(default=1)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="tasks")
    categories: List["Category"] = Relationship(back_populates="tasks", link_model="TaskCategory")
    time_logs: List["TimeLog"] = Relationship(back_populates="task")

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    tasks: List[Task] = Relationship(back_populates="categories", link_model="TaskCategory")

class TaskCategory(SQLModel, table=True):
    task_id: Optional[int] = Field(default=None, foreign_key="task.id", primary_key=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id", primary_key=True)
    association_priority: int = Field(default=1)

class TimeLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None 
    task: Optional[Task] = Relationship(back_populates="time_logs")

class Schedule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    date: datetime
    description: Optional[str] = None
    user: Optional[User] = Relationship(back_populates="schedules")
```

- Users (пользователи)
- Tasks (задачи, one-to-many с Users и many-to-many с Categories)
- Categories (категории)
- TaskCategories (ассоциативная таблица с extra полем association_priority)
- TimeLogs (логи времени, one-to-many с Tasks)
- Schedules (расписания, one-to-many с Users)

4. В `schemas.py` создаем Pydantic-схемы для валидации

5. Настраиваем соединения с БД и миграций

```python
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import AsyncEngine
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

6. Инициализируем Alembic и создаем миграции

7. Реализуем CRUD и роутеры

8. Реализуем авторизацию

```python
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

9. Запускаем `uvicorn main:app --reload`

10. Тестируем с помощью Swagger

# Вывод

В рамках данной работы реализовано серверное приложение на FastAPI для тайм-менеджмента.
Спроектирована и реализована реляционная БД PostgreSQL. Внедрена аутентификация по JWT-токенам.