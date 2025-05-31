# Отчет по практикам по лабораторной работе №1

Мной были выполнены три практики. Каждая практика направлена на освоение основных инструментов для разработки API с использованием FastAPI, работы с базой данных через SQLModel, настройки миграций с Alembic, работы с переменными окружения и структуры проекта.

## Практика 1.1: Создание базового приложения на FastAPI

**Цель:**  
Создать минимальное FastAPI-приложение с одним GET-эндпоинтом и автодокументацией Swagger.

**Что сделано:**

- Создан новый проект в IDE и инициализировано виртуальное окружение.
- Установлены зависимости: `fastapi[all]` и `uvicorn`.
- Реализован файл `main.py` с базовым экземпляром приложения FastAPI и одним эндпоинтом.

## Практика 1.2: Настройка БД, SQLModel и миграции через Alembic

**Цель:**
Настроить подключение к базе данных PostgreSQL, реализовать модели данных через SQLModel и обеспечить миграции с помощью Alembic.

**Что сделано:**

- Создан файл .env с переменными окружения, включая URL подключения к базе данных.
- Реализован файл connection.py для загрузки переменных окружения, создания подключения и функций init_db() и get_session().
```
import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv()

db_url = os.getenv("DB_ADMIN")
engine = create_engine(db_url, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```
- Созданы модели данных в файле models.py (включая модели для воинов, умений, профессий и т.д.). Пример модели для война:
```
class Warrior(WarriorDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profession: Optional[Profession] = Relationship(back_populates="warriors_prof")
    skills: List[Skill] = Relationship(back_populates="warriors", link_model=SkillWarriorLink)
```
- Настроены миграции с Alembic:
    - Инициализирован Alembic с командой `alembic init migrations`.
    - Настроен файл env.py для загрузки переменных окружения и использования метаданных моделей.

## Практика 1.3: Миграции, ENV, GitIgnore и структура проекта

**Цель:**
Организовать проект, используя переменные окружения, настроить Alembic для миграций, создать файл .gitignore и структурировать проект по модулям.

**Что сделано:**

- Создан файл .env с конфигурацией:
```DB_ADMIN=postgresql://postgres:123@localhost:5433/warriors_db```
- Создан файл .gitignore, в котором исключены файлы виртуального окружения, файлы компиляции Python, IDE-файлы и .env.


