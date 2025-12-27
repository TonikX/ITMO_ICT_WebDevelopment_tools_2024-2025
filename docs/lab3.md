# Лабораторная работа 3. Docker, очередь задач и интеграция парсера

> Упаковать FastAPI-приложение, БД и парсер в контейнеры Docker; добавить HTTP-вызов парсера и асинхронный вызов через очередь Celery+Redis.

## Содержание

* [Цель](#цель)
* [Структура проекта](#структура-проекта)
* [Подзадача 1: Docker и Docker Compose](#подзадача-1-docker-и-docker-compose)
* [Подзадача 2: HTTP-вызов парсера](#подзадача-2-http-вызов-парсера)
* [Подзадача 3: Парсер через очередь Celery](#подзадача-3-парсер-через-очередь-celery)
* [Запуск и проверка](#запуск-и-проверка)

---

## Цель

Научиться упаковывать FastAPI-приложение, базу данных и парсер данных в Docker-контейнеры; вызывать парсер через HTTP и через очередь Celery+Redis.

## Структура проекта

```bash
lab3/
├─ app/                      # FastAPI-приложение (из ЛР1)
│  ├─ main.py                # end‑to‑end приложение с /parse и /tasks
│  ├─ api/                   # маршруты для данных и парсера
│  ├─ models.py              # ORM-модели
│  └─ utils.py               # функции запуска парсинга
├─ parser/                   # отдельное приложение-парсер (из ЛР2)
│  └─ parse.py               # функции parse_url(url)
├─ docker/                   # конфигурация Docker
│  ├─ Dockerfile.app         # сборка FastAPI-приложения
│  ├─ Dockerfile.parser      # сборка контейнера для парсера
│  └─ docker-compose.yml     # оркестрация сервисов
├─ celery_app/               # конфигурация Celery
│  ├─ celery.py              # инициализация Celery-брокера и воркера
│  └─ tasks.py               # задача parse_task(url)
└─ README.md                 # Инструкции по сборке и запуску
```

## Подзадача 1: Docker и Docker Compose

1. **Dockerfile для FastAPI** (`docker/Dockerfile.app`):

   ```dockerfile
   FROM python:3.10-slim
   WORKDIR /app
   COPY lab1/app/requirements.txt .
   RUN pip install -r requirements.txt
   COPY lab1/app/ ./app
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```
2. **Dockerfile для парсера** (`docker/Dockerfile.parser`):

   ```dockerfile
   FROM python:3.10-slim
   WORKDIR /parser
   COPY lab2/scripts/requirements.txt .
   RUN pip install -r requirements.txt
   COPY lab2/scripts/parse_*.py .
   CMD ["python", "parse_asyncio.py"]  # пример, можно адаптировать
   ```
3. **docker-compose.yml** (`docker/docker-compose.yml`):

   ```yaml
   version: '3.8'
   services:
     db:
       image: postgres:15
       environment:
         POSTGRES_USER: user
         POSTGRES_PASSWORD: pass
         POSTGRES_DB: finances
       volumes:
         - db_data:/var/lib/postgresql/data

     app:
       build:
         context: ./docker
         dockerfile: Dockerfile.app
       depends_on:
         - db
       environment:
         DATABASE_URL: postgresql://user:pass@db:5432/finances
         REDIS_URL: redis://redis:6379/0
       ports:
         - "8000:8000"

     parser:
       build:
         context: ./docker
         dockerfile: Dockerfile.parser
       depends_on:
         - db

     redis:
       image: redis:7

     worker:
       build:
         context: ./celery_app
       command: celery -A celery_app.celery worker --loglevel=info
       depends_on:
         - redis
         - app

   volumes:
     db_data:
   ```

## Подзадача 2: HTTP-вызов парсера

Добавьте в FastAPI-приложение (`app/api/parser.py`) маршрут:

```python
from fastapi import APIRouter, HTTPException
import requests

router = APIRouter()

@router.post("/parse")
def parse_url(url: str):
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = parser.parse_url(url)
        return {"status": "ok", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Подзадача 3: Парсер через очередь Celery

1. **Настройка Celery** (`celery_app/celery.py`):

   ```python
   from celery import Celery
   import os

   celery = Celery(
     "tasks",
     broker=os.getenv("REDIS_URL"),
     backend=os.getenv("REDIS_URL")
   )
   ```
2. **Задача** (`celery_app/tasks.py`):

   ```python
   from .celery import celery
   from parser.parse import parse_url

   @celery.task(bind=True)
   def parse_task(self, url: str):
       return parse_url(url)
   ```
3. **HTTP-маршрут для фоновой задачи** (`app/api/async_parser.py`):

   ```python
   from fastapi import APIRouter
   from celery.result import AsyncResult
   from celery_app.tasks import parse_task

   router = APIRouter()

   @router.post("/tasks/parse")
   def enqueue_parse(url: str):
       task = parse_task.delay(url)
       return {"task_id": task.id}

   @router.get("/tasks/{task_id}")
   def get_status(task_id: str):
       result = AsyncResult(task_id)
       return {"status": result.status, "result": result.result}
   ```

## Запуск и проверка

1. Перейдите в папку `docker` и запустите:

   ```bash
   docker-compose up --build
   ```
2. Дождитесь поднятия всех сервисов (db, redis, app, parser, worker).
3. **Проверка HTTP-парсера**:

   ```bash
   curl -X POST http://localhost:8000/parse -d '"https://example.com"'
   ```
4. **Проверка фоновой задачи**:

   ```bash
   curl -X POST http://localhost:8000/tasks/parse -d '"https://example.com"'
   curl http://localhost:8000/tasks/<task_id>
   ```

---

