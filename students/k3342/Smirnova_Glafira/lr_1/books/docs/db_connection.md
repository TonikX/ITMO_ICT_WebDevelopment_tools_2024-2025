# Соединение с PostgreSQL

В проекте реализована инициализация БД при запуске приложения, создание и заполнение таблиц при первом запуске, а также
подгрузка переменных из файла .env.

`app/main.py`
```python
@app.on_event("startup")
def on_startup():
    init_db()
```

Автоматическая инициализация базы при старте приложения.

---

`app/db/base.py`
```python
from sqlmodel import SQLModel, Session, select

from app.db.genres import DEFAULT_GENRES
from app.models import *
from app.db.session import engine

def init_db():
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        statement = select(Genre)
        existing_genres = session.exec(statement).all()

        if not existing_genres:
            for name in DEFAULT_GENRES:
                session.add(Genre(name=name))
            session.commit()
```

`SQLModel.metadata.create_all(engine)` — создаёт все таблицы в базе данных, если они ещё не существуют.

Затем создаётся сессия для работы с БД.

Если в таблице Genre нет жанров, то они добавляются из списка `DEFAULT_GENRES`.

---


`app/db/session.py`
```python
from sqlmodel import Session, create_engine

from app.core.config import settings

engine = create_engine(settings.DB_ADMIN, echo=False)

def get_session():
    with Session(engine) as session:
        yield session
```

Создаётся `engine` — объект подключения к базе PostgreSQL.

Строка подключения берётся из переменной окружения `settings.DB_ADMIN` (см. ниже).

`get_session()` создаёт сессию и безопасно её закрывает после использования (через `yield`), используется как зависимость.

---

`app/core/config.py`
```python

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8
    DB_ADMIN: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

Класс `Settings` использует `pydantic-settings` для загрузки переменных из файла `.env`.
