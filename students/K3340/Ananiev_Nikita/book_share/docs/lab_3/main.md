# Лабораторная работа 3: Упаковка FastAPI приложения в Docker, Работа с источниками данных и Очереди

## Цель

Научиться упаковывать FastAPI приложение в Docker, интегрировать парсер данных с базой данных и вызывать парсер через API и очередь.

После выполнения всех 3-х подзадач, итоговый docker-compose файл выглядит следующим образом:
```yaml
version: '3'

services:
  app:
    container_name: app_container
    build: .
    ports:
      - "8000:8080"
    env_file:
      - .env
    depends_on:
      - db

  parser:
    container_name: parser_container
    build: ./parser
    ports:
      - "8001:4242"
    env_file:
      - ./parser/parser.env
    depends_on:
      - db

  celery:
    container_name: celery_container
    build: .
    command: celery -A endpoints.celery_tasks worker --loglevel=info
    env_file:
      - .env
    depends_on:
      - app
      - parser
      - db

  db:
    container_name: db_container
    image: postgres:alpine
    environment:
      POSTGRES_PASSWORD: ${DB_PASS}
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: postgres
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: [ "CMD-SHELL", "pg_isready -U postgres -d ${DB_NAME}" ]
      interval: 2s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  pgdata: {}
  redis_data: {}

```