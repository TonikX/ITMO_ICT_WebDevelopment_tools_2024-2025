# Лабораторная работа 3: Упаковка FastAPI приложения в Docker, Работа с источниками данных и Очереди

## Цель
Научиться упаковывать FastAPI приложение в Docker, интегрировать парсер данных с базой данных и вызывать парсер через API и очередь.

## Подзадача 1: Упаковка FastAPI приложения, базы данных и парсера данных в Docker

### Dockerfile для `app`

Базовый образ: python:3.10-slim.

Копируются все исходники в /usr/src, устанавливаются зависимости из app/requirements.txt.

Команда запуска: uvicorn app.main:app --host 0.0.0.0 --port 8000.

Порт 8000 проброшен наружу.

```dockerfile
FROM python:3.10-slim

WORKDIR /usr/src

COPY . .

RUN pip install --no-cache-dir -r app/requirements.txt

EXPOSE 8000

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
```

### Dockerfile для `parser`

Базовый образ: python:3.10-slim.

Рабочая папка /usr/src/parser.

Устанавливаются зависимости из parser_service/requirements.txt.

Запуск: uvicorn main:app --host 0.0.0.0 --port 8001.

```dockerfile
FROM python:3.10-slim

WORKDIR /usr/src/parser

COPY parser_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY parser_service/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Dockerfile для `celery`

Базовый образ: python:3.11-slim.

Копируется весь проект, устанавливаются зависимости из celery_app/requirements.txt.

Команда: celery -A celery_app.tasks worker --loglevel=info.

```dockerfile
FROM python:3.11-slim
WORKDIR /usr/src

COPY . .

RUN pip install --no-cache-dir -r celery_app/requirements.txt

CMD ["celery", "-A", "celery_app.tasks", "worker", "--loglevel=info"]
```


### `docker-compose.yml`

Описаны 5 сервисов: db, redis, web, parser, celery_worker.

Зависимости (depends_on) гарантируют порядок старта.

Общие переменные окружения (.env) прокидываются в web, parser и celery_worker.

Volume pgdata хранит данные PostgreSQL вне контейнера.


```yml
version: '3.8'

services:
  db:
    image: postgres:15
    restart: always
    environment:
      POSTGRES_USER: book_user
      POSTGRES_PASSWORD: supersecretpassword
      POSTGRES_DB: book_exchange
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    restart: always
    ports:
      - "6379:6379"

  web:
    build:
      context: .
      dockerfile: Dockerfile
    restart: always
    env_file: .env
    depends_on:
      - db
      - parser
      - redis
    ports:
      - "8000:8000"

  parser:
    build:
      context: .
      dockerfile: Dockerfile.parser
    restart: always
    env_file: .env
    depends_on:
      - db
    ports:
      - "8001:8001"

  celery_worker:
    build:
      context: .
      dockerfile: Dockerfile.celery
    restart: always
    env_file: .env
    depends_on:
      - redis
      - parser

volumes:
  pgdata:
```

## Подзадача 2: Вызов парсера из FastAPI

**Эндпоинт /parse в сервисе parser**
Вход: JSON { "url": "<ссылка>" }.

Логика:

Открытие асинхронного соединения с БД (AsyncDBFiller.connect()).

Загрузка страницы через aiohttp, разбор parse_book_details.

Запись одной книги в bookinfo, на основе ключей таблицы.

Выход: {"message":"Parsing completed","url":...}.

**Эндпоинт /parse-all**
Автоматически обходит поисковые страницы Gutenberg (сортированные по скачиваниям),

Составляет список ссылок на книги,

Делит их на чанки по 4 воркера,

Каждый воркер загружает страницы книг и массово добавляет записи.

Возвращает общее число сохраненных записей.

### Эндпоинт в `parser/main.py`

```python
import os
import time
import asyncio
from typing import List
from aiohttp import ClientSession
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from parser import tpl, base, parse_book_links, parse_book_details
from db import AsyncDBFiller

DB_CONN = os.getenv("DATABASE_URL")

WORKERS = 4
BOOKS_TOTAL = 100

app = FastAPI()

class ParseRequest(BaseModel):
    url: str

@app.post("/parse")
async def parse_endpoint(req: ParseRequest):
    filler = AsyncDBFiller(dsn=DB_CONN)
    await filler.connect()
    try:
        async with ClientSession() as session:
            resp = await session.get(req.url)
            html = await resp.text()
            details = parse_book_details(html)
            await filler.add_book(details, source="async")
        return {"message": "Parsing completed", "url": req.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await filler.disconnect()

@app.post("/parse-all")
async def parse_all():
    filler = AsyncDBFiller(dsn=DB_CONN)
    await filler.connect()
    try:
        async with ClientSession() as session:
            pages = [base + tpl.format(i) for i in range(1, BOOKS_TOTAL+1, 25)]
            tasks = [session.get(url) for url in pages]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            links = []
            for r in results:
                if not isinstance(r, Exception):
                    html = await r.text()
                    links.extend(parse_book_links(html))
                    await r.release()

            per = (len(links) + WORKERS - 1) // WORKERS
            chunks = [links[i:i+per] for i in range(0, len(links), per)]
            workers = [
                worker(chunk, session, filler)
                for chunk in chunks
            ]
            saved_counts: List[int] = await asyncio.gather(*workers)
        return {"saved_total": sum(saved_counts)}
    finally:
        await filler.disconnect()

async def worker(chunk: List[str], session: ClientSession, filler: AsyncDBFiller) -> int:
    saved = 0
    for url in chunk:
        try:
            resp = await session.get(url)
            html = await resp.text()
            details = parse_book_details(html)
            if await filler.add_book(details, source="async"):
                saved += 1
            await resp.release()
        except:
            continue
    return saved
```


## Подзадача 3: Вызов парсера из FastAPI через очередь

### Конфигурация Celery (`parser/celeryconfig.py`)

Конфигурация Celery (celery_app/celeryconfig.py)
broker_url и result_backend указывают на Redis.

JSON‐сериализация и часовой пояс UTC.

```python
import os

broker_url = f"redis://{os.getenv('REDIS_HOST','redis')}:{os.getenv('REDIS_PORT','6379')}/0"
result_backend = broker_url

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]

timezone = "UTC"
enable_utc = True
```

### Задачи (`parser/tasks.py`)

Задача parse_url (celery_app/tasks.py)
Bind=True позволяет внутри делать self.retry().

Отсылает HTTP-запрос к сервису парсера.

При ошибке автоматически повторяет до 3 раз с задержкой.

```python
import os
import requests
from celery import Celery

app = Celery(
    "parser_tasks",
    broker=f"redis://{os.getenv('REDIS_HOST','redis')}:{os.getenv('REDIS_PORT','6379')}/0",
    backend=f"redis://{os.getenv('REDIS_HOST','redis')}:{os.getenv('REDIS_PORT','6379')}/0",
)

app.config_from_object("celery_app.celeryconfig")

@app.task(bind=True, name="parse_url")
def parse_url(self, url: str):
    try:
        resp = requests.post("http://parser:8001/parse", json={"url": url}, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10, max_retries=3)
```

### Эндпоинты очереди (`app/routers/books.py`)

Эндпоинты в web
POST /books/parse-sync — прямой вызов HTTP-парсера.

POST /books/parse-async — parse_url.delay(url), возвращает task_id.

GET /books/parse-status/{task_id} — через AsyncResult проверяет состояние и результат.

```python
@router.post("/parse-sync", status_code=status.HTTP_202_ACCEPTED)
def parse_sync(url: str):
    try:
        resp = requests.post("http://parser:8001/parse", json={"url": url}, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Parser sync error: {e}")
    
@router.post("/parse-async", status_code=status.HTTP_202_ACCEPTED)
def parse_async(url: str):
    task = parse_url.delay(url)
    return {"task_id": task.id}

@router.get("/parse-status/{task_id}")
def parse_status(task_id: str):
    result = AsyncResult(task_id, app=parse_url.app)
    return {
        "state": result.state,
        "result": result.result if result.ready() else None
    }
```

### Тестирование и результаты
Поднял все сервисы командой
```
docker compose up --build
```

## Выводы

В результате получена распределённая система из трёх контейнеров (API, парсер, воркер) с общей БД и очередью задач, готовая к масштабированию и развертыванию в любых окружениях. Это соответствует современным практикам микросервисной архитектуры и DevOps-подходу.