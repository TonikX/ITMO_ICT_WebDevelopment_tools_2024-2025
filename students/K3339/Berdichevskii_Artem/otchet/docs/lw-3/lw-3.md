# Лабораторная работа №3

## Цель

Разработка и контейнеризация веб-приложения на **FastAPI** с интеграцией парсера и асинхронной обработкой задач с использованием **Celery** и **Redis**.

---

## 1. Упаковка FastAPI, базы данных и парсера в Docker

### 1.1 docker-compose.yaml

```yaml
version: "3.9"

services:
  fastapi:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      - redis

  celery_worker:
    build:
      context: .
      dockerfile: docker/Dockerfile
    command: celery -A app.celery_worker.celery_app worker --loglevel=info
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      - redis

  redis:
    image: redis:alpine
```

### Синхронный вызов

```python
@app.post("/parse-direct")
def parse_direct(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return {"message": "Parsed directly", "length": len(response.text)}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Асинхронный вызов

```python
@app.post("/parse-async")
def parse_async(url: str):
    task = parse_url_task.delay(url)
    return {"message": "Parsing started", "task_id": task.id}
```

## Реализация парсера

```python
import requests

def fetch_page_content(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text
```

## Интеграция с Celery

```python
from celery import Celery
from app.parser import fetch_page_content
import os

celery_app = Celery(
    "tasks",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
)

@celery_app.task
def parse_url_task(url: str):
    content = fetch_page_content(url)
    return f"Parsed {len(content)} characters"
```

### Celery Worker

```python
from app.tasks import celery_app

# Вызов из docker:
# celery -A app.celery_worker.celery_app worker --loglevel=info
```

![1](pic/3_1.png)

![2](pic/3_2.png)

![3](pic/3_3.png)