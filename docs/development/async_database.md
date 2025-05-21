# Асинхронная работа с базой данных

В проекте реализована поддержка асинхронной работы с базой данных PostgreSQL с использованием `asyncpg` и асинхронного API SQLAlchemy.

## Настройка асинхронного подключения

Асинхронное подключение к базе данных настраивается в файле `async_connection.py`:

```python
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

load_dotenv()
username = os.getenv("DB_USERNAME", "postgres")
password = os.getenv("DB_PASSWORD", "")
host = os.getenv("DB_HOST", "localhost")
database = os.getenv("DB_NAME", "web_team_finder")

# Асинхронный URL для подключения к PostgreSQL
async_db_url = f'postgresql+asyncpg://{username}:{password}@{host}/{database}'

# Создаем асинхронный движок
async_engine = create_async_engine(
    async_db_url,
    echo=True,
    future=True
)

# Создаем фабрику асинхронных сессий
async_session_factory = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_async_db():
    """Инициализирует асинхронную базу данных"""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_async_session():
    """Возвращает асинхронную сессию базы данных"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
```

## Использование асинхронной сессии в FastAPI

Асинхронная сессия базы данных может быть использована в FastAPI с помощью системы зависимостей:

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Skill
from async_connection import get_async_session

app = FastAPI()

@app.get("/async/skills/")
async def get_skills(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Skill))
    skills = result.scalars().all()
    return skills
```

## Выполнение запросов

Асинхронные запросы к базе данных выполняются с использованием ключевого слова `await`:

```python
# Получение данных
result = await session.execute(select(Skill).where(Skill.id == skill_id))
skill = result.scalars().first()

# Добавление данных
session.add(skill)
await session.commit()
await session.refresh(skill)

# Удаление данных
await session.delete(skill)
await session.commit()
```

## Преимущества асинхронной работы с базой данных

1. **Эффективное использование ресурсов**: Асинхронные запросы позволяют освободить поток выполнения во время ожидания ответа от базы данных.
2. **Масштабируемость**: Возможность обрабатывать больше одновременных запросов с меньшим количеством ресурсов.
3. **Совместимость с асинхронным кодом**: Естественная интеграция с другими асинхронными операциями, такими как HTTP-запросы.

## Пример использования в парсере веб-страниц

```python
async def parse_and_save(url, http_session, db_session):
    async with http_session.get(url) as response:
        html = await response.text()
        # Обработка HTML
        
        # Асинхронное сохранение в базу данных
        skill = Skill(name="Extracted skill", description=url)
        db_session.add(skill)
        await db_session.commit()
```

## Миграции с асинхронной базой данных

Для управления схемой асинхронной базы данных по-прежнему используется Alembic, так как миграции выполняются отдельно от основного приложения. Конфигурация миграций остается такой же, как и для синхронного подключения.