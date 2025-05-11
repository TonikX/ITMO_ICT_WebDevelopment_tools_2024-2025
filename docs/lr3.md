# 📦 Документация к проекту с Docker, FastAPI, Celery, PostgreSQL и Redis

## 🐳 Docker Compose

```yaml
version: "3.9"

services:
  db:
    image: postgres:16-alpine
    container_name: my_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: dbname
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    container_name: redis
    restart: unless-stopped
    ports:
      - "6379:6379"

  parser:
    image: parser-image:latest
    container_name: parser
    restart: unless-stopped
    ports:
      - "8001:8001"
    environment:
      PGHOST: db
      PGPORT: 5432
      PGUSER: user
      PGPASSWORD: password
      PGDATABASE: dbname
    depends_on: [db, redis]

  celery-worker:
    image: parser-image:latest
    container_name: parser_celery_worker
    restart: unless-stopped
    command: celery -A celery_app worker -l info
    environment:
      PGHOST: db
      PGPORT: 5432
      PGUSER: user
      PGPASSWORD: password
      PGDATABASE: dbname
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/1
    depends_on: [db, redis]

  api:
    image: main-app-image:latest
    container_name: api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      PARSER_URL: http://parser:8001
      DATABASE_URL: postgresql://user:password@db/dbname
    depends_on: [parser, celery-worker]
```

---

## ⚙️ Описание контейнеров

| Контейнер       | Назначение                            |
| --------------- | ------------------------------------- |
| `db`            | PostgreSQL база данных                |
| `redis`         | Брокер и бэкенд для Celery            |
| `parser`        | FastAPI-приложение для парсинга URL   |
| `celery-worker` | Обработка фоновых задач (парсинг)     |
| `api`           | Основное FastAPI-приложение с роутами |

---

## 🚀 Команды для запуска

```bash
docker-compose up --build
```

---

## 📡 Примеры запросов

#### 🔐 Регистрация

```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
-H "Content-Type: application/json" \
-d '{"username": "testuser", "email": "test@example.com", "password": "secret"}'
```

#### 🔑 Авторизация

```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=testuser&password=secret"
```

#### 📂 Получить категории

```bash
curl -X GET "http://127.0.0.1:8000/finance/categories" \
-H "Authorization: Bearer $JWT_TOKEN"
```

#### 🧾 Синхронный парсинг категорий

```bash
curl -X POST http://localhost:8000/finance/categories/parse \
     -H "Content-Type: application/json" \
     -d '{"urls": ["https://assistentus.ru/okved/razdel-a/", "https://assistentus.ru/okved/razdel-b/"]}'
```

#### 🕒 Асинхронный парсинг (через Celery)

```bash
curl -X POST http://localhost:8000/finance/categories/parse_async \
     -H "Content-Type: application/json" \
     -d '{"urls": ["https://assistentus.ru/okved/razdel-c/", "https://assistentus.ru/okved/razdel-d/"]}'
```

#### 🔄 Проверка статуса задачи

```bash
curl -X GET http://localhost:8000/finance/categories/parse_tasks/TASK_ID
```

---

## 🐍 Dockerfile (FastAPI-приложение)

```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "serve:app", "--host", "0.0.0.0", "--port", "8001"]
```
