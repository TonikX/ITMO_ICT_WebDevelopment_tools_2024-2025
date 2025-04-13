# Лабораторная работа №1 Реализация серверного приложения FastAPI

Цели

Научится реализовывать полноценное серверное приложение с помощью фреймворка FastAPI с применением дополнительных средств и библиотек.

**Тема: Разработка веб-приложения для буккросинга.**

Ваша задача - создать веб-приложение, которое позволит пользователям обмениваться книгами между собой. Это приложение должно облегчать процесс обмена книгами, позволяя пользователям находить книги, которые им интересны, и находить новых пользователей для обмена книгами. 

**Функционал веб-приложения должен включать следующее:**

**Создание профилей**: Возможность пользователям создавать профили, указывать информацию о себе, своих навыках, опыте работы и предпочтениях по проектам.

**Добавление книг в библиотеку**: Пользователи могут добавлять книги, которыми они готовы поделиться, в свою виртуальную библиотеку на платформе.

**Поиск и запросы на обмен**: Функционал поиска книг в библиотеке других пользователей. Возможность отправлять запросы на обмен книгами другим пользователям.

**Управление запросами и обменами**: Возможность просмотра и управления запросами на обмен. Возможность подтверждения или отклонения запросов на обмен.


**Критерии модели данных:**

1. 5 или больше таблиц
2. Связи many-to-many и one-to-many
3. Ассоциативная сущность должна иметь поле, характеризующее связь, помимо ссылок на связанные таблицы

![](images/web.drawio(1).png)

## Создание базы данных

### Создание бд в postgres 
1. через win+r services.msc запускаю postgres.
2. в cmd psql -U postgres
3. CREATE DATABASE book_exchange;

### Создание моделей

**код из файла models.py:**
```python
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


# ---------- USER ----------
class User(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    profile_info: Optional[str] = None
    skills: Optional[str] = None
    preferences: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    books: List["UserBook"] = Relationship(back_populates="user")
    sent_requests: List["ExchangeRequest"] = Relationship(back_populates="sender", sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.sender_id]"})
    received_requests: List["ExchangeRequest"] = Relationship(back_populates="receiver", sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.receiver_id]"})


# ---------- BOOK ----------
class Book(SQLModel, table=True):
    book_id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str
    isbn: Optional[str] = None
    genre: str
    publication_year: int
    condition: str
    description: Optional[str] = None

    owners: List["UserBook"] = Relationship(back_populates="book")


# ---------- USERBOOK ----------
class UserBook(SQLModel, table=True):
    user_book_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.user_id")
    book_id: int = Field(foreign_key="book.book_id")
    added_at: datetime = Field(default_factory=datetime.utcnow)
    status: str  # доступна / недоступна
    location: Optional[str] = None

    user: "User" = Relationship(back_populates="books")
    book: "Book" = Relationship(back_populates="owners")

    sender_requests: List["ExchangeRequest"] = Relationship(back_populates="sender_book", sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.sender_book_id]"})
    receiver_requests: List["ExchangeRequest"] = Relationship(back_populates="desired_book", sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.desired_book_id]"})


# ---------- EXCHANGEREQUEST ----------
class ExchangeRequest(SQLModel, table=True):
    request_id: Optional[int] = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="user.user_id")
    receiver_id: int = Field(foreign_key="user.user_id")
    sender_book_id: int = Field(foreign_key="userbook.user_book_id")
    desired_book_id: int = Field(foreign_key="userbook.user_book_id")
    status: str  # pending / accepted / rejected
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    message: Optional[str] = None

    sender: "User" = Relationship(back_populates="sent_requests", sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.sender_id]"})
    receiver: "User" = Relationship(back_populates="received_requests", sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.receiver_id]"})
    sender_book: "UserBook" = Relationship(back_populates="sender_requests", sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.sender_book_id]"})
    desired_book: "UserBook" = Relationship(back_populates="receiver_requests", sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.desired_book_id]"})
    exchange: Optional["Exchange"] = Relationship(back_populates="request")


# ---------- EXCHANGE ----------
class Exchange(SQLModel, table=True):
    exchange_id: Optional[int] = Field(default=None, primary_key=True)
    request_id: int = Field(foreign_key="exchangerequest.request_id", unique=True)
    exchange_date: datetime = Field(default_factory=datetime.utcnow)
    completion_status: str  # в процессе / завершен
    user1_rating: Optional[int] = None
    user2_rating: Optional[int] = None
    feedback: Optional[str] = None

    request: "ExchangeRequest" = Relationship(back_populates="exchange")
```
### Создание файла для бд

**код из файла db.py:**
```python
from sqlmodel import Session, SQLModel, create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

```
Всю важную информацию храню в файле .env
### Создание базы данных с моделями

**код из файла create_db.py:**
```python
from models import SQLModel
from db import engine

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    create_db_and_tables()

```

Запускаю python create_db.py в терминале
![](images/db_create.png)
Проверяю в постгрес
![](images/db_done.png)


## Миграции Alembic
Редактирую файл env.py
![](images/envchange.png)
В терминале запускаю alembic revision --autogenerate -m "Initial migration"
![](images/mig1.png)
Применяю миграции с помощью alembic upgrade head
![](images/migcommit.png)

## Запуск приложения
В командной строке ввожу uvicorn main:app --reload
![](images/upload.png)

по пути http://127.0.0.1:8000
![](images/check.png)
по пути http://127.0.0.1:8000/docs
![](images/docs.png)

## Эндпоинты

Создаю папку api
![](images/api.png)
**Пример кода из файла books.py**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from db import get_session
from models import Book, User
from schemas.book import BookCreate, BookRead, BookUpdate
from api.dependencies import get_current_user

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/", response_model=BookRead)
def create_book(
        book: BookCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    db_book = Book.from_orm(book)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@router.get("/", response_model=List[BookRead])
def read_books(
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session)
):
    books = session.exec(select(Book).offset(skip).limit(limit)).all()
    return books


@router.get("/{book_id}", response_model=BookRead)
def read_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.patch("/{book_id}", response_model=BookRead)
def update_book(
        book_id: int,
        book: BookUpdate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    book_data = book.dict(exclude_unset=True)
    for key, value in book_data.items():
        setattr(db_book, key, value)

    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@router.delete("/{book_id}")
def delete_book(
        book_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    session.delete(db_book)
    session.commit()
    return {"ok": True}
```
Создаю папку schemas
![](images/schemas.png)
**Пример кода из файла book.py**
```python
from pydantic import BaseModel
from typing import Optional

class BookBase(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    genre: str
    publication_year: int
    condition: str
    description: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookRead(BookBase):
    book_id: int

    class Config:
        orm_mode = True

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    genre: Optional[str] = None
    publication_year: Optional[int] = None
    condition: Optional[str] = None
    description: Optional[str] = None
```
## Пример работы энпоинтов
Просмотр юзера
![](images/readuser.png)
Создание книги
![](images/createbook.png)
Регистрация
![](images/register.png)
Получение токена
![](images/token.png)














**код из файла models.py:**
```python

```








































## Практика

### Практика 1.1. Создание базового приложения на FastAPI

Установка FastApi с cопутствующими библиотеками в командной строке с помощью команды:

pip install fastapi[all]

**по пути 127.0.0.1:8000**
![](images/1.png)
**по пути 127.0.0.1:8000/docs**
![](images/2.png)
![](images/3.png)
**Запрос всех воинов:**
![](images/4.png)
**Добавление воина:**
![](images/5.png)
**Удаление воина:**
![](images/6.png)
**Редактирование воина:**
![](images/7.png)
**После обновления кода для представлений изменилась документация к разработанному API (127.0.0.1:8000/docs). Теперь для каждого запроса отображается описание в каком формате передаются и принимаются данные для каждого реализованного метода.**
![](images/8.png)
![](images/9.png)
![](images/10.png)
![](images/11.png)


### Практика 1.2. Настройка БД, SQLModel и миграции через Alembic

pip install sqlmodel

**код из файла db.py:**
```python
from sqlmodel import SQLModel, Session, create_engine

db_url = 'postgresql://postgres:Arina2992@localhost:5432/warriors_db'
engine = create_engine(db_url, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

```

**код из файла models.py:**
```python
from enum import Enum
from typing import Optional, List

#from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship


class RaceType(Enum):
    director = "director"
    worker = "worker"
    junior = "junior"


class SkillWarriorLink(SQLModel, table=True):
    skill_id: Optional[int] = Field(
        default=None, foreign_key="skill.id", primary_key=True
    )
    warrior_id: Optional[int] = Field(
        default=None, foreign_key="warrior.id", primary_key=True
    )


class Skill(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = ""
    warriors: Optional[List["Warrior"]] = Relationship(back_populates="skills", link_model=SkillWarriorLink)


class Profession(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    description: str
    warriors_prof: List["Warrior"] = Relationship(back_populates="profession")


class Warrior(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    race: RaceType
    name: str
    level: int
    profession_id: Optional[int] = Field(default=None, foreign_key="profession.id")
    profession: Optional[Profession] = Relationship(back_populates="warriors_prof")
    skills: Optional[List[Skill]] = Relationship(back_populates="warriors", link_model=SkillWarriorLink)

```
Чтобы описанные таблицы были созданы необходимо добавить в main.py специальный метод on_startup с декоратором on_event вызывающий внутри их инициализацию. 

```python
@app.on_event("startup")
def on_startup():
    init_db()

```
После запуска приложения в консоли вывелся SQL-запрос на создание сущностей, описанных в models.py

```sq
CREATE TABLE skill (
        id SERIAL NOT NULL,
        name VARCHAR NOT NULL,
        description VARCHAR,
        PRIMARY KEY (id)
)

CREATE TABLE profession (
        id SERIAL NOT NULL,
        title VARCHAR NOT NULL,
        description VARCHAR NOT NULL,
        PRIMARY KEY (id)
)

CREATE TABLE warrior (
        id SERIAL NOT NULL,
        race racetype NOT NULL,
        name VARCHAR NOT NULL,
        level INTEGER NOT NULL,
        profession_id INTEGER,
        PRIMARY KEY (id),
        FOREIGN KEY(profession_id) REFERENCES profession (id)
)

CREATE TABLE skillwarriorlink (
        skill_id INTEGER NOT NULL,
        warrior_id INTEGER NOT NULL,
        PRIMARY KEY (skill_id, warrior_id),
        FOREIGN KEY(skill_id) REFERENCES skill (id),
        FOREIGN KEY(warrior_id) REFERENCES warrior (id)
)

```

### Практика 1.3. Миграции, ENV, GitIgnore и структура проекта

Для интеграции Alembic в разрабатываемый проект необходимо его установить через пакетный менеджер: 

pip install alembic  

Реализация механизма миграций происходит через вызов alembic init [name] в командной строке, где [name] — название папки, хранящей настройки миграций. Сгенерируем папку с миграциями и сопутствующие файлы настроек:

alembic init migrations 

В корне проекта, помимо ранее созданных файлов должна сформироваться следующая структура
![](images/structure.png)

Сгенерировалась папка migratgions хранящая внутри себя папку с файлами миграций versions, файл окружения БД env.py и шаблон генерации миграций script.py.mako. В корне проекта добавился файл настроек alembic.ini

**код из файла env.py:**
```python
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from models import *

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
#target_metadata = None

target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

```
