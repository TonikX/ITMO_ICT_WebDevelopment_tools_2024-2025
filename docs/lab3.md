# Архитектура проекта с Celery и FastAPI

Проект состоит из нескольких сервисов, управляемых через Docker Compose:

## Сервисы

- **db** – PostgreSQL база данных.
- **redis** – брокер сообщений для Celery.
- **parser** – сервис для парсинга HTML страниц.
- **hackathon** – основной FastAPI-приложение.
- **celery_worker** – воркер Celery для асинхронной обработки задач.

---

## Celery задачи

### 1. `parse_url_tasks`

- Асинхронно парсит одну страницу.
- Использует `httpx.AsyncClient` для загрузки HTML.
- Отправляет HTML на сервис `parser` для извлечения данных.

### 2. `parse_all_urls`

- Асинхронно обрабатывает список URL из `urls`.
- Вызывает `_parse_url` для каждого URL и собирает результаты.

---

## FastAPI роуты

### `POST /parse-url`

- Параметр: `url`  
- Создаёт задачу Celery `parse_url_tasks`.
- Возвращает `task_id`.

### `POST /parse-all`

- Создаёт задачу Celery `parse_all_urls`.
- Возвращает `task_id`.

### `GET /task-status/{task_id}`

- Проверяет статус задачи Celery по `task_id`.
- Если готово — возвращает `status: completed` и результат.
- Если ещё выполняется — возвращает `status: pending`.

---

## Особенности

- Асинхронность через `asyncio` и `httpx`.
- Celery использует Redis как брокер и backend.
- Парсер работает в отдельном сервисе, чтобы разгрузить основной API.
