# Подзадача 3: Вызов парсера из FastAPI через очередь

## 1. `celery_app.py` - файл, который содержит настройки Celery и определение задачи для парсинга
```python
import requests
from bs4 import BeautifulSoup
from celery import Celery
from core import settings
from core.database import SessionLocal
from models.parsed_sites import ParsedSites

celery_app = Celery(
    "parser_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)
```
Здесь создается экземпляр Celery и задаются параметры брокера и бэкенда для хранения результатов выполнения задач.
```python
celery_app.conf.update(
    timezone='Europe/Moscow',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    max_retries=5,
)
```
Конфигурация Celery, которая включает в себя настройки таймзоны и поведение при сбоях
```python
@celery_app.task()
def parse_and_save(url) -> None:
    with SessionLocal() as session:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string if soup.title else 'No title'

            url = ParsedSites(url=url, title=title)
            session.add(url)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
```
Эта функция parse_and_save выполняет парсинг URL, извлекает заголовок и сохраняет результат в базу данных. В случае ошибки транзакция откатывается.

## docker-compose.yml - данный файл конфигурации описывает все сервисы: приложение, базы данных, Redis и workers для Celery.
```docker-compose
services:
  db:
    image: postgres:17.5-alpine3.21
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - type: tmpfs
        target: /dev/shm
        tmpfs:
          size: 128m
    ports:
      - ${POSTGRES_PORT}:${POSTGRES_PORT}
    healthcheck:
      ...
```
Определяется сервис базы данных PostgreSQL с переменными окружения и настройками проверки работоспособности
```docker-compose
  app:
    build:
      context: .
    command: sh -c "alembic upgrade head && sleep 5 && uvicorn main:app --host 0.0.0.0 --port ${APP_PORT}"
    depends_on:
      db:
        condition: service_healthy
        restart: true
    ports:
      - ${APP_PORT}:${APP_PORT}
    environment:
      CELERY_BROKER_URL: "redis://${REDIS_HOST}:${REDIS_PORT}/0"
      CELERY_RESULT_BACKEND: "redis://${REDIS_HOST}:${REDIS_PORT}/0"
    env_file: ".env"
```
Настройки для основного приложения FastAPI, где указываются параметры для подключения к Redis как к брокеру Celery.
```docker-compose
  redis:
    image: redis:8.0.1-alpine
    ports:
      - ${REDIS_PORT}:${REDIS_PORT}

  workers:
    build:
      context: .
    command: sh -c "celery -A celery_app worker -l INFO"
    depends_on:
      - redis
      - app
    environment:
      CELERY_BROKER_URL: "redis://${REDIS_HOST}:${REDIS_PORT}/0"
      CELERY_RESULT_BACKEND: "redis://${REDIS_HOST}:${REDIS_PORT}/0"
    env_file: ".env"
```
Настройка Redis как брокера и определение службы workers для выполнения задач Celery.

## Dockerfile 
```Dockerfile
FROM python:3.13.3-alpine

WORKDIR /usr/src/app

RUN apk --no-cache add postgresql-dev

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
```

## Итог
В результате реализации подзадачи 3 был создан асинхронный механизм вызова парсера через очередь задач Celery, что обеспечивает более надежную и масштабируемую архитектуру приложения. Используя Redis как брокер сообщений, можно эффективно управлять задачами и обрабатывать их в фоне, не блокируя основной поток выполнения FastAPI. Это улучшает производительность и отзывчивость приложения, позволяя обрабатывать множество запросов одновременно.