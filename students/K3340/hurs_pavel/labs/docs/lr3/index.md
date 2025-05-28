# Лабораторная работа №3: Микросервисная архитектура

## Описание проекта

Данный проект представляет собой микросервисное приложение для парсинга веб-страниц. Приложение состоит из нескольких сервисов:

1. **Web Service** (FastAPI) - основной веб-сервис, предоставляющий API для взаимодействия с пользователем
2. **Parser Service** (FastAPI) - сервис для парсинга веб-страниц
3. **Celery Worker** - сервис для асинхронной обработки задач
4. **PostgreSQL** - база данных для хранения результатов парсинга
5. **Redis** - брокер сообщений для Celery

## Архитектура проекта

```
LR3/
├── docker-compose.yml
├── parser_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── parser_api.py
│   ├── models/
│   │   └── parsed_url.py
│   ├── migrations/
│   │   ├── versions/
│   │   └── env.py
│   └── alembic.ini
└── web_service/
    ├── Dockerfile
    ├── requirements.txt
    ├── main.py
    └── celery_worker.py
```

## API Endpoints

### 1. Синхронный парсинг URL

**Endpoint:** `/parse/sync`  
**Method:** POST  
**Request:**
```json
{
    "urls": [
        "https://www.python.org",
        "https://fastapi.tiangolo.com",
        "https://www.djangoproject.com"
    ]
}
```

**Response:**
```json
[
    {
        "url": "https://www.python.org",
        "title": "Welcome to Python.org",
        "status": "completed"
    },
    {
        "url": "https://fastapi.tiangolo.com",
        "title": "FastAPI - FastAPI",
        "status": "completed"
    },
    {
        "url": "https://www.djangoproject.com",
        "title": "Django: The Web framework for perfectionists with deadlines",
        "status": "completed"
    }
]
```

### 2. Асинхронный парсинг URL

**Endpoint:** `/parse/async`  
**Method:** POST  
**Request:**
```json
{
    "urls": [
        "https://github.com",
        "https://www.postgresql.org",
        "https://redis.io"
    ]
}
```

**Response:**
```json
{
    "task_id": "e02bf9de-dad9-4c89-bbb6-7290b1a10cdf"
}
```

### 3. Проверка статуса задачи

**Endpoint:** `/parse/status/{task_id}`  
**Method:** GET  
**Response:**
```json
{
    "status": "completed",
    "result": [
        {
            "url": "https://github.com",
            "title": "GitHub: Let's build from here",
            "status": "completed"
        },
        {
            "url": "https://www.postgresql.org",
            "title": "PostgreSQL: The world's most advanced open source database",
            "status": "completed"
        },
        {
            "url": "https://redis.io",
            "title": "Redis: The open source, in-memory data store used by millions of developers",
            "status": "completed"
        }
    ]
}
```

## Запуск проекта

1. Сборка и запуск контейнеров:
```bash
docker-compose build
docker-compose up -d
```

2. Проверка статуса сервисов:
```bash
docker-compose ps
```

## Тестирование

### 1. Проверка доступности API документации:
```bash
curl http://localhost:8000/docs
```

### 2. Тестирование синхронного парсинга:
```bash
curl -X POST http://localhost:8000/parse/sync \
     -H "Content-Type: application/json" \
     -d '{"urls": ["https://www.python.org", "https://fastapi.tiangolo.com"]}'
```

### 3. Тестирование асинхронного парсинга:
```bash
curl -X POST http://localhost:8000/parse/async \
     -H "Content-Type: application/json" \
     -d '{"urls": ["https://github.com", "https://www.postgresql.org"]}'
```

### 4. Проверка статуса асинхронной задачи:
```bash
curl http://localhost:8000/parse/status/e02bf9de-dad9-4c89-bbb6-7290b1a10cdf
```

## Процесс разработки

1. Создана базовая структура проекта с микросервисной архитектурой
2. Настроена конфигурация Docker и Docker Compose
3. Реализован парсер-сервис с использованием FastAPI
4. Настроена база данных PostgreSQL и миграции с помощью Alembic
5. Реализован веб-сервис с синхронным и асинхронным API
6. Настроен Celery для асинхронной обработки задач
7. Настроен Redis как брокер сообщений
8. Проведено тестирование всех компонентов системы

## Результаты тестирования

Все основные компоненты системы работают корректно:

1. **Web Service**:
   - API документация доступна
   - Синхронный и асинхронный эндпоинты работают
   - Проверка статуса задач работает

2. **Parser Service**:
   - Успешно парсит URL
   - Миграции базы данных работают
   - Интеграция с веб-сервисом работает

3. **Celery Worker**:
   - Обрабатывает асинхронные задачи
   - Интеграция с Redis работает
   - Результаты задач сохраняются и доступны

4. **База данных**:
   - PostgreSQL запущен
   - Таблицы созданы
   - Данные успешно сохраняются и извлекаются

5. **Redis**:
   - Сервис запущен и доступен
   - Используется Celery для очереди задач