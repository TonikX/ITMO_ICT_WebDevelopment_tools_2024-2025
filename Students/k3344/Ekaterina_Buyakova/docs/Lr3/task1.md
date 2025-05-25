# Подзадача 1: Упаковка FastAPI приложения, базы данных и парсера данных в Docker

## Dockerfile для приложения FastAPI
Файл `Dockerfile` в каталоге `/app` используется для упаковки FastAPI приложения в Docker контейнер.

```dockerfile
FROM python:3.13.3-alpine

ARG APP_PORT=8000

WORKDIR /usr/src/app

RUN apk --no-cache add postgresql-dev

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD alembic upgrade head && sleep 5 && uvicorn main:app --host 0.0.0.0 --port ${APP_PORT}
```
- **FROM python:3.13.3-alpine:** задает базовый образ для контейнера, минимальный размер и быстрое время загрузки
- **WORKDIR /usr/src/app:** устанавливает рабочую директорию в контейнере
- **RUN apk --no-cache add postgresql-dev:** устанавливает необходимые зависимости для работы с PostgreSQL
- **COPY requirements.txt ./:** копирует файл зависимостей в контейнер
- **RUN pip install --no-cache-dir -r requirements.txt:** устанавливает зависимости из requirements.txt
- **COPY . .:** копирует весь код приложения в контейнер
- **CMD:** выполняет миграции базы данных и запускает приложение с помощью Uvicorn

## Dockerfile для парсера
```dockerfile
FROM python:3.13.3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD uvicorn main:app --host 0.0.0.0 --port ${PARSER_PORT}
```
Аналогично, здесь используется базовый образ Python, установка зависимостей и запуск парсера данных через Uvicorn.

## Парсер данных
Код парсера находится в файле main.py, который реализует HTTP API для выполнения запросов на парсинг
```python
import logging
import os
import aiohttp
import asyncpg
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()
```
- **load_dotenv():** загружает переменные окружения из .env файла
- **FastAPI():** создает экземпляр FastAPI приложения
- **logging:** настраивает логирование для отладки

### Функции парсера
1. get_db_connection() - устанавливает асинхронное соединение с базой данных PostgreSQL, используя учетные данные из переменных окружения
```python
async def get_db_connection():
    return await asyncpg.connect(
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database=os.getenv("POSTGRES_DB"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
    )
```
2. ensure_table_exists(conn) - проверяет и создает таблицу для хранения парсинга, если она не существует
```python
async def ensure_table_exists(conn):
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS async (
            id serial PRIMARY KEY,
            url text,
            title text
        )
    ''')
```
3. parse_and_save(url) - выполняет запрос на указанный URL, парсит HTML с помощью BeautifulSoup и сохраняет результат в базе данных
```python
async def parse_and_save(url: str) -> str | None:
    ...
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            ...
            await conn.execute(
                "INSERT INTO async (url, title) VALUES ($1, $2)",
                url, title
            )
```
4. HTTP эндпоинт - который позволяет выполнять парсинг через HTTP-запросы
```python
@app.get("/parse/")
async def parse(url: str):
```

## Файл docker-compose 
- **parser:** определяет сервис для парсера, его зависимости и порты
- **db:** настраивает сервис базы данных Postgres с необходимыми переменными окружения и проверкой здоровья
- **app:** определяет сервис для основного FastAPI приложения, указывая на его зависимости

## Итог
В ходе выполнения подзадачи 1 было создано приложение FastAPI, которое обеспечивают возможность работы с парсером данных и базой данных PostgreSQL. Использование Docker и Docker Compose позволяет легко управлять зависимостями и процессом развертывания, что делает систему более устойчивой и удобной для разработки.