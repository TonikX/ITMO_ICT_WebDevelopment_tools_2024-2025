# Отчет по лабораторной работе №2

## Dockerfile для контейнера api

```Dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN chmod +x /app/start.sh
CMD ["/app/start.sh"]
```

где ```start.sh``` для запуска миграций alembic
```bash
#!/bin/bash

sleep 5
alembic upgrade head
uvicorn main:app --host 0.0.0.0 --port 8000
```

Скрипт необходим для проведения миграций и запуска сервиса в команде старта контейнера.

## Dockerfile для парсера

```
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY .. .

CMD ["uvicorn", "serve:app", "--host", "0.0.0.0", "--port", "18000"]
```

## Итоговый docker-compose

Который состоит из:

1. База данных для системы (Postgres)

2. Кэш база данных (redis), которая используется как очередь задач для Celery

3. Сервис парсера для работы с Celery

4. Воркер Celery

5. Основной сервис (API)


```yaml
services:
  lr3_pg:
    image: postgres:16-alpine
    container_name: lr3_pg
    restart: unless-stopped
    environment:
      POSTGRES_USER: lr3
      POSTGRES_PASSWORD: 12345678
      POSTGRES_DB: lr3
    ports:
      - "15432:5432"

  redis:
    image: redis:7-alpine
    container_name: redis
    restart: unless-stopped
    ports:
      - "6379:6379"

  parser:
    image: tasks_parser:mock
    container_name: parser
    restart: unless-stopped
    ports:
      - "18000:18000"
    environment:
      DB_URL: postgresql://lr3:12345678@lr3_pg:5432/lr3
    depends_on:
      - lr3_pg
      - redis

  celery-worker:
    image: tasks_parser:mock
    container_name: parser_celery_worker
    restart: unless-stopped
    command: celery -A celery_app worker -l info
    environment:
      DB_URL: postgresql://lr3:12345678@lr3_pg:5432/lr3
    depends_on:
      - lr3_pg
      - redis

  api:
    image: hackathon-app:latest
    container_name: api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      PARSER_URL: http://parser:18000
      DATABASE_URL: postgresql://lr3:12345678@lr3_pg:15432/lr3
    depends_on:
      - parser
      - celery-worker
```

## Работа с Celery

Модуль для запуск тасок на парсинг данных по списку урлов

```python
from celery import Celery

from parsing_async import run

REDIS_BROKER = "redis://redis:6379/0"
REDIS_BACKEND = "redis://redis:6379/1"

celery_app = Celery(
    "tasks",
    broker=REDIS_BROKER,
    backend=REDIS_BACKEND,
)

@celery_app.task(name="task.parse_urls")
def parse_urls_task(urls: list[str]) -> dict:
    elapsed_time = run(urls)
    return {"elapsed_sec": elapsed_time, "saved": len(urls)}
```

И эндпоинты для запуска задач парсера

```python
@app.post("/parse")
async def parse(payload: URLList):
    if not payload.urls:
        raise HTTPException(400, "Empty urls")

    d = await run(payload.urls)
    return {"elapsed_sec": d, "saved": len(payload.urls)}


@app.post("/parse_async")
def enqueue_parse(req: URLList):
    if not req.urls:
        raise HTTPException(400, "Empty urls")
    job = parse_urls_task.delay(req.urls)
    return {"task_id": job.id, "status": "queued"}


@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    res: AsyncResult = celery_app.AsyncResult(task_id)
    if res.state == "PENDING":
        return {"status": "pending"}
    if res.state == "SUCCESS":
        return {"status": "done", "result": res.result}
    if res.state == "FAILURE":
        return {"status": "failed", "error": str(res.result)}
    return {"status": res.state.lower()}

```