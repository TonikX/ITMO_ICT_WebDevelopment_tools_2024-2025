# Лабораторная работа №7

## 1) Установить Celery и Redis:

```python
celery_app = Celery(
    "parser",
    broker="redis://lr5-redis-1:6379/0",
    backend="redis://lr5-redis-1:6379/0"
)

@celery_app.task
def parse_url_task(url: str):
    return parse_link(url)
```

## 2) Обновить Docker Compose файл:

```docker
services:
  timemanager:
    build:
      context: ./TimeManager
    container_name: timemanager
    ports:
      - "8000:8000"
    depends_on:
      - db
    env_file:
      - ./TimeManager/.env

  parser:
    build:
      context: ./parser
    container_name: parser
    ports:
      - "9000:9000"
    depends_on:
      - db
      - redis
    env_file:
      - ./parser/.env
  worker:
    build:
      context: ./parser
    container_name: parser-worker
    command: celery -A worker.celery_app worker --loglevel=info
    depends_on:
      - parser
      - redis
      - db
    env_file:
      - .env
  db:
    image: "postgres:17.2"
    container_name: postgres
    restart: always
    env_file:
      - .env
  redis:
    image: "redis:latest"
    ports:
      - "6379:6379"
```

## 3) Эндпоинт для асинхронного вызова парсера

```python
@app.post("/parse-async")
async def parse_direct(url: str):
    try:
        count = await parse_link(url)
        return {"message": "Парсинг завершён", "added": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка парсинга: {e}")
```