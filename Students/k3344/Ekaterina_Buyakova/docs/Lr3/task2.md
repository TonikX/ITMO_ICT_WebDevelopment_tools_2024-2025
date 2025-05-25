# Подзадача 2: Вызов парсера из FastAPI

В данной подзадаче был реализован эндпоинт в приложении FastAPI для вызова парсера, который запущен в отдельном контейнере. Этот функционал позволяет пользователям отправлять запросы с URL для парсинга и получать результаты.

## Файл `app/routers/api.py`
Здесь содержится реализация эндпоинта FastAPI, который принимает URL для парсинга и взаимодействует с парсером по сокету.

```python
import socket
from core import settings
from fastapi import Depends, APIRouter

router = APIRouter()
```
Для начала  импортируются необходимые библиотеки и создается экземпляр APIRouter.
```python
def get_socket() -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        sock.connect((settings.PARSER_HOST, settings.PARSER_PORT))
        return sock
    except socket.error as err:
        sock.close()
        raise err
```
Функция get_socket создает сокет, устанавливает соединение с парсером и возвращает его. Обработка ошибок позволяет закрыть сокет в случае неудачи.
```python
@router.get("/")
def parse_url(url: str = "", sock: socket.socket = Depends(get_socket)):
    result = {}
    url += "\n"
    try:
        print(url.encode())
        sock.sendall(url.encode("utf-8"))
        recv_data = sock.recv(1024)
        result = {"url": url, "data": recv_data.decode("utf-8")}
    except socket.timeout:
        result = {"message": "timeout"}
    except socket.error as e:
        result = {"message": f"error: {e}"}
    finally:
        sock.close()
    return result
```
Эндпоинт parse_url принимает параметр url, отправляет его парсеру по сокету и возвращает ответ. Если произошла ошибка, возвращается соответствующее сообщение.

## Файл `app/Dockerfile`
```Dockerfile
FROM python:3.13.3-alpine
ARG APP_PORT=8000
WORKDIR /usr/src/app

RUN apk --no-cache add postgresql-dev

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD alembic upgrade head && sleep 5 && uvicorn main:app --host 0.0.0.0 --port ${APP_PORT}
```
В этом файле мы собираем образ приложения FastAPI, устанавливаем зависимости и запускаем приложение через uvicorn.

## Файл `app/main.py`. Здесь создается экземпляр FastAPI и подключаются маршруты:
```python
from fastapi import FastAPI
from core import settings
from routers import api

app = FastAPI(
    title="Сервис управления финансами",
    description="API для управления личными финансами",
    version="1.0.0"
)

app.include_router(api.router, prefix="/api", tags=["API"])
```

## Файл `parser/Dockerfile`, где собирается образ парсера и запускается основной скрипт
```Dockerfile
FROM python:3.13.3-alpine
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./main.py"]
```

## `parser/main.py` - jсновной файл для парсера, который будет выполнять парсинг URL
````python
import asyncio
import logging
import os
from asyncio import StreamWriter, StreamReader
from urllib.parse import urlparse
import aiohttp
import asyncpg
from bs4 import BeautifulSoup
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
````
Импортируются необходимые библиотеки и настраивается система логирования
````python
async def parse_and_save(writer: StreamWriter, session: aiohttp.ClientSession, db_pool: asyncpg.pool.Pool, url: str):
    ...
    async with session.get(url) as response:
      ...
````
Функция parse_and_save выполняет HTTP GET запрос к указанному URL, парсит HTML и сохраняет результат в базу данных PostgreSQL. Используются асинхронные методы для повышения производительности.

## docker-compose.yml - файл конфигурации для сборки всех сервисов
```docker-compose
services:
  parser:
    build:
      context: parser/.
    depends_on:
      db:
        condition: service_healthy
        restart: true
    ports:
      - ${PARSER_PORT}:${PARSER_PORT}
    env_file: ".env"

  db:
    image: postgres:17.5-alpine3.21
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_DB=${POSTGRES_DB}
    ...
    
  app:
    build:
      context: app/.
    depends_on:
      db:
        condition: service_healthy
        restart: true
      parser:
        condition: service_started
    ports:
      - ${APP_PORT}:${APP_PORT}
    env_file: ".env"
```
В этом файле определяются все сервисы: приложение, парсер и база данных. Указываются зависимости, порты и конфигурация окружения.

## Итог
В ходе реализации подзадачи 2 был создан эндпоинт в FastAPI, который принимает URL для парсинга от клиента и взаимодействует с парсером, запущенным в отдельном контейнере. Это позволяет интегрировать функциональность парсинга в веб-приложение, предоставляя пользователям возможность запускать парсинг через API. Были использованы сокеты для взаимодействия между сервисами и асинхронность для эффективного выполнения запросов и обработки данных.