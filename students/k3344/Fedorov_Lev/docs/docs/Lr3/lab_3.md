# Лабораторная работа 3: Контейнеризация и микросервисная архитектура

## Архитектура системы

### Микросервисы:
- **FastAPI App** (`fastapi`) - основное API приложение
- **Parser Service** (`parser`) - сервис для парсинга данных
- **Celery Worker** (`celery_worker`) - обработчик асинхронных задач
- **PostgreSQL** (`postgres`) - база данных
- **Redis** (`redis`) - брокер сообщений для Celery
- **Flower** (`flower`) - мониторинг Celery

### Схема взаимодействия:
```
[Client] → [FastAPI] → [Parser Service]
    ↓           ↓
[PostgreSQL] [Redis] → [Celery Worker]
                            ↓
                      [Flower Monitor]
```

## Структура проекта

```
lab_3/
├── app/                          # Основное FastAPI приложение
│   ├── routes/
│   │   ├── parser/              # Роутеры для парсера
│   │   │   ├── parse_routes.py  # HTTP интеграция с парсером
│   │   │   └── celery_routes.py # Celery очереди
│   │   └── ...                  # Остальные роутеры
│   ├── models.py                # Модели SQLAlchemy
│   ├── config.py                # Конфигурация
│   └── urls.py                  # Главный файл FastAPI
├── parsers/                     # Парсеры (из лаб. работы 1)
│   ├── async_parser_sports.py
│   ├── threading_parser_sports.py
│   └── multiprocessing_parser_sports.py
├── docker-compose.yml           # Описание всех сервисов
├── fastapi.Dockerfile          # Docker образ для FastAPI
├── parser.Dockerfile           # Docker образ для парсера
├── parser_app.py               # FastAPI приложение парсера
├── celery_app.py               # Конфигурация Celery
├── Makefile                    # Команды для управления
├── start.sh                    # Скрипт запуска
├── test_api.sh                 # Тесты API
└── example_usage.py            # Демонстрация функций
```

## Docker конфигурация

### docker-compose.yml

Основной файл для оркестрации всех сервисов:

```yaml
services:
  # База данных PostgreSQL
  postgres:
    image: postgres:15
    container_name: hockey_postgres
    environment:
      POSTGRES_DB: hockey_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: tochange
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis для очередей
  redis:
    image: redis:7-alpine
    container_name: hockey_redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Основное FastAPI приложение
  fastapi:
    build:
      context: .
      dockerfile: fastapi.Dockerfile
    container_name: hockey_fastapi
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:tochange@postgres:5432/hockey_db
      - REDIS_URL=redis://redis:6379
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
```

### Dockerfile'ы

**fastapi.Dockerfile:**
```dockerfile
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Создание директорий для файлов
RUN mkdir -p /app/uploads/player_photos \
    && mkdir -p /app/uploads/player_certificates \
    && mkdir -p /app/uploads/team_logos

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.urls:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**parser.Dockerfile:**
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y gcc g++ curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY parser_requirements.txt .
RUN pip install --no-cache-dir -r parser_requirements.txt

COPY parsers/ ./parsers/
COPY parser_app.py .

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8001

CMD ["uvicorn", "parser_app:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
```

## Задача 2: HTTP интеграция сервисов

### Parser Service (parser_app.py)

Отдельный FastAPI сервис для парсинга данных:

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import subprocess
import asyncio

app = FastAPI(
    title="Hockey Parser API",
    description="API для парсинга спортивных данных",
    version="1.0.0"
)

class ParseRequest(BaseModel):
    urls: List[HttpUrl]
    parser_type: str = "async"  # async, threading, multiprocessing

@app.post("/parse")
async def parse_sports_data(request: ParseRequest, background_tasks: BackgroundTasks):
    """Запускает парсинг спортивных данных"""
    import uuid
    task_id = str(uuid.uuid4())
    
    # Определяем какой парсер использовать
    parser_files = {
        "async": "async_parser_sports.py",
        "threading": "threading_parser_sports.py", 
        "multiprocessing": "multiprocessing_parser_sports.py"
    }
    
    parser_file = parser_files.get(request.parser_type, "async_parser_sports.py")
    
    # Запускаем парсинг в фоне
    background_tasks.add_task(run_parser_task, task_id, parser_file, request.urls)
    
    return {
        "task_id": task_id,
        "status": "started",
        "message": f"Parsing task started with {request.parser_type} parser"
    }
```

### HTTP интеграция в FastAPI (parse_routes.py)

Роутер для взаимодействия с сервисом парсера:

```python
from fastapi import APIRouter, HTTPException, Depends
import httpx

router = APIRouter(prefix="/parser", tags=["parser"])

PARSER_URL = "http://parser:8001"  # Docker service name

@router.post("/parse")
async def start_parsing(request: ParseRequest, current_user: User = Depends(get_current_admin_user)):
    """Запускает парсинг данных через внешний сервис парсера"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{PARSER_URL}/parse",
                json=request.dict()
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Parser service unavailable: {str(e)}"
        )

@router.get("/status/{task_id}")
async def get_parsing_status(task_id: str):
    """Получает статус задачи парсинга"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{PARSER_URL}/status/{task_id}")
        response.raise_for_status()
        return response.json()
```

### Пример использования HTTP интеграции:

```bash
# 1. Получаем токен авторизации
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# 2. Запускаем парсинг через FastAPI → Parser
curl -X POST "http://localhost:8000/parser/parse" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://www.nhl.com/teams"],
    "parser_type": "async"
  }'

# Ответ:
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "started", 
  "message": "Parsing task started with async parser"
}

# 3. Проверяем статус
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/parser/status/123e4567-e89b-12d3-a456-426614174000"

# Ответ:
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "message": "Parsing completed successfully",
  "teams_parsed": 32,
  "schools_created": 32,
  "tournaments_created": 1
}
```

## Задача 3: Асинхронные очереди Celery

### Конфигурация Celery (celery_app.py)

```python
from celery import Celery
import os

# Настройка Celery
celery_app = Celery(
    "hockey_parser",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379")
)

# Конфигурация
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_result_expires=3600,  # 1 час
)

@celery_app.task(bind=True, name='parse_sports_data')
def parse_sports_data_task(self, urls: List[str], parser_type: str = "async"):
    """Celery задача для парсинга спортивных данных"""
    try:
        # Обновляем статус задачи
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Starting parser service request...'}
        )
        
        # Выполняем HTTP запрос к парсеру
        import requests
        parser_url = "http://parser:8001"
        
        response = requests.post(
            f"{parser_url}/parse",
            json={"urls": urls, "parser_type": parser_type},
            timeout=30
        )
        response.raise_for_status()
        
        parser_task = response.json()
        parser_task_id = parser_task["task_id"]
        
        # Ждем завершения парсинга (polling)
        max_wait_time = 300  # 5 минут
        wait_time = 0
        
        while wait_time < max_wait_time:
            time.sleep(5)
            wait_time += 5
            
            status_response = requests.get(
                f"{parser_url}/status/{parser_task_id}",
                timeout=10
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                
                if status_data["status"] == "completed":
                    return {
                        'status': 'completed',
                        'message': 'Parsing completed successfully',
                        'teams_parsed': status_data.get('teams_parsed', 0),
                        'schools_created': status_data.get('schools_created', 0),
                        'tournaments_created': status_data.get('tournaments_created', 0)
                    }
                elif status_data["status"] == "failed":
                    return {
                        'status': 'failed',
                        'message': f'Parsing failed: {status_data.get("message", "Unknown error")}'
                    }
                else:
                    # Обновляем прогресс
                    self.update_state(
                        state='PROGRESS',
                        meta={'status': f'Parser status: {status_data["status"]}'}
                    )
        
        # Таймаут
        return {'status': 'timeout', 'message': 'Parsing task timed out'}
        
    except Exception as e:
        return {'status': 'failed', 'message': f'Task execution error: {str(e)}'}
```

### Celery роутер (celery_routes.py)

```python
from fastapi import APIRouter, HTTPException, Depends
from celery.result import AsyncResult
from ...celery_app import celery_app

router = APIRouter(prefix="/queue", tags=["queue"])

@router.post("/parse")
async def queue_parsing_task(request: QueueParseRequest, current_user: User = Depends(get_current_admin_user)):
    """Ставит задачу парсинга в очередь Celery"""
    try:
        urls_str = [str(url) for url in request.urls]
        
        # Запускаем задачу в Celery
        task = celery_app.send_task(
            'parse_sports_data',
            args=[urls_str, request.parser_type]
        )
        
        return {
            "task_id": task.id,
            "status": "queued",
            "message": f"Parsing task queued with {request.parser_type} parser"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue task: {str(e)}")

@router.get("/status/{task_id}")
async def get_queue_task_status(task_id: str):
    """Получает статус задачи из очереди Celery"""
    try:
        result = AsyncResult(task_id, app=celery_app)
        
        if result.state == 'PENDING':
            return {"task_id": task_id, "status": "pending", "message": "Task is waiting in queue"}
        elif result.state == 'PROGRESS':
            return {"task_id": task_id, "status": "progress", "message": "Task is in progress", "result": result.info}
        elif result.state == 'SUCCESS':
            return {"task_id": task_id, "status": "success", "message": "Task completed successfully", "result": result.result}
        elif result.state == 'FAILURE':
            return {"task_id": task_id, "status": "failure", "message": f"Task failed: {str(result.info)}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")
```

### Пример использования Celery очередей:

```bash
# 1. Добавляем задачу в очередь
curl -X POST "http://localhost:8000/queue/parse" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://www.nhl.com/teams"],
    "parser_type": "async"
  }'

# Ответ:
{
  "task_id": "f49bc007-98e6-4b1d-a27b-6924c7ef933b",
  "status": "queued",
  "message": "Parsing task queued with async parser"
}

# 2. Проверяем статус в очереди
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/queue/status/f49bc007-98e6-4b1d-a27b-6924c7ef933b"

# Возможные ответы:
# Ожидание:
{"task_id": "...", "status": "pending", "message": "Task is waiting in queue"}

# В процессе:
{"task_id": "...", "status": "progress", "message": "Task is in progress"}

# Завершено:
{
  "task_id": "f49bc007-98e6-4b1d-a27b-6924c7ef933b",
  "status": "success",
  "message": "Task completed successfully",
  "result": {
    "status": "completed",
    "teams_parsed": 32,
    "schools_created": 32,
    "tournaments_created": 1
  }
}

# 3. Проверяем активные задачи
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/queue/active"

# 4. Статистика очередей
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/queue/stats"
```

## Скрипты управления

### Makefile

Удобные команды для управления Docker:

```makefile
# Сборка всех образов
build:
	docker-compose build

# Запуск всех сервисов
up:
	docker-compose up -d

# Остановка всех сервисов
down:
	docker-compose down

# Перезапуск всех сервисов
restart:
	docker-compose restart

# Просмотр логов
logs:
	docker-compose logs -f

# Логи конкретного сервиса
logs-fastapi:
	docker-compose logs -f fastapi

logs-parser:
	docker-compose logs -f parser

logs-celery:
	docker-compose logs -f celery_worker

# Очистка
clean:
	docker-compose down -v
	docker system prune -f

# Полная пересборка
rebuild:
	docker-compose down -v
	docker-compose build --no-cache
	docker-compose up -d

# Проверка статуса
status:
	docker-compose ps

# Тестирование
test-api:
	curl -X GET http://localhost:8000/health

test-parser:
	curl -X GET http://localhost:8001/health
```

### start.sh

Автоматический скрипт запуска:

```bash
#!/bin/bash

echo "Запуск Hockey API с Docker"

# Проверяем Docker
if ! command -v docker &> /dev/null; then
    echo "Docker не установлен!"
    exit 1
fi

# Создаем .env если не существует
if [ ! -f .env ]; then
    echo "Создание .env файла..."
    cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://postgres:tochange@postgres:5432/hockey_db
DB_HOST=postgres
DB_NAME=hockey_db
DB_USER=postgres
DB_PASSWORD=tochange
REDIS_URL=redis://redis:6379
SECRET_KEY=your-secret-key-change-in-production
EOF
fi

# Создаем директории
mkdir -p uploads/player_photos uploads/player_certificates uploads/team_logos

# Запускаем
docker-compose down
docker-compose build
docker-compose up -d

# Ждем запуска
sleep 10

echo "Сервисы запущены!"
echo "Доступные URL:"
echo "FastAPI:     http://localhost:8000"
echo "Swagger:     http://localhost:8000/docs"
echo "Parser:      http://localhost:8001" 
echo "Flower:      http://localhost:5555"
```

### test_api.sh

Автоматическое тестирование всех компонентов:

```bash
#!/bin/bash

echo "🧪 Тестирование Hockey API"

BASE_URL="http://localhost:8000"
PARSER_URL="http://localhost:8001"

# Функция проверки ответа
check_response() {
    if [ $1 -eq 200 ]; then
        echo -e "PASSED"
    else
        echo -e "FAILED (HTTP $1)"
    fi
}

# Тест основных эндпоинтов
echo "🔍 1. Проверка базовых эндпоинтов"
echo -n "FastAPI Health Check: "
response=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/health)
check_response $response

echo -n "Parser Health Check: "
response=$(curl -s -o /dev/null -w "%{http_code}" $PARSER_URL/health)
check_response $response

# Аутентификация
echo "2. Тестирование аутентификации"
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123")

if echo $TOKEN_RESPONSE | grep -q "access_token"; then
    echo "Токен получен"
    TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
else
    echo "Ошибка аутентификации"
    exit 1
fi

# Тест парсера (HTTP интеграция)
echo "3. Тестирование парсера (Задача 2)"
PARSE_RESPONSE=$(curl -s -X POST "$BASE_URL/parser/parse" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://httpbin.org/json"], "parser_type": "async"}')

if echo $PARSE_RESPONSE | grep -q "task_id"; then
    echo "HTTP интеграция работает"
    TASK_ID=$(echo $PARSE_RESPONSE | grep -o '"task_id":"[^"]*"' | cut -d'"' -f4)
    
    sleep 2
    STATUS_RESPONSE=$(curl -s "$BASE_URL/parser/status/$TASK_ID" \
      -H "Authorization: Bearer $TOKEN")
    echo "Статус: $(echo $STATUS_RESPONSE | grep -o '"status":"[^"]*"' | cut -d'"' -f4)"
else
    echo "HTTP интеграция не работает"
fi

# Тест Celery очередей
echo " 4. Тестирование очередей (Задача 3)"
QUEUE_RESPONSE=$(curl -s -X POST "$BASE_URL/queue/parse" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://httpbin.org/json"], "parser_type": "async"}')

if echo $QUEUE_RESPONSE | grep -q "task_id"; then
    echo "Celery очереди работают"
    QUEUE_TASK_ID=$(echo $QUEUE_RESPONSE | grep -o '"task_id":"[^"]*"' | cut -d'"' -f4)
    
    sleep 3
    QUEUE_STATUS=$(curl -s "$BASE_URL/queue/status/$QUEUE_TASK_ID" \
      -H "Authorization: Bearer $TOKEN")
    echo "Статус очереди: $(echo $QUEUE_STATUS | grep -o '"status":"[^"]*"' | cut -d'"' -f4)"
else
    echo " Celery очереди не работают"
fi

echo "Тестирование завершено!"
```

## Результаты тестирования

Ваши тесты показали отличные результаты:

```
Тестирование Hockey API
==========================
1. Проверка базовых эндпоинтов
=================================
FastAPI Health Check: PASSED
FastAPI Root: PASSED
Swagger Docs: PASSED
Parser Health Check: PASSED
Parser Root: PASSED

🔐 2. Тестирование аутентификации
=================================
Получение токена: PASSED
Token получен: eyJhbGciOiJIUzI1NiIs...

👤 3. Тестирование пользователей
===============================
Профиль пользователя: PASSED
Список пользователей: PASSED

 4. Тестирование основных сущностей
====================================
Список команд: PASSED
Список игроков: PASSED
Список турниров: PASSED
Список сезонов: PASSED

 5. Тестирование парсера (Задача 2)
====================================
Здоровье парсера через API: PASSED
Тест запуска парсинга: PASSED
Task ID: 4066f822-a45b-497f-83d7-fb9a54449d1d
Статус задачи парсинга: PASSED

⚡ 6. Тестирование очередей (Задача 3)
=====================================
Активные задачи Celery: PASSED
Статистика очередей: PASSED
Запуск задачи в очереди: PASSED
Queue Task ID: f49bc007-98e6-4b1d-a27b-6924c7ef933b
Статус задачи из очереди: PASSED

 7. Результаты тестирования
=============================
Всего тестов выполнено: приблизительно 15+
```

## Ключевые достижения

### Задача 1: Контейнеризация Docker
- Все сервисы упакованы в контейнеры
- Используется Docker Compose для оркестрации
- Настроены health checks для всех сервисов
- Правильно настроены сети и volumes
- Персистентность данных обеспечена

### Задача 2: HTTP интеграция сервисов
- Parser выделен в отдельный микросервис
- FastAPI взаимодействует с Parser через HTTP API
- Реализована обработка ошибок и таймаутов
- Асинхронное выполнение задач парсинга
- Мониторинг статуса задач

### Задача 3: Асинхронные очереди Celery
- Redis как брокер сообщений
- Celery Worker для обработки задач
- Flower для мониторинга очередей
- Интеграция Celery с FastAPI
- Отслеживание прогресса выполнения

## 🌐 Интерфейсы и мониторинг

- **FastAPI Swagger**: http://localhost:8000/docs
- **Parser API**: http://localhost:8001
- **Flower Monitor**: http://localhost:5555
- **PostgreSQL**: localhost:5433
- **Redis**: localhost:6379

## 🔧 Команды для работы

```bash
# Запуск системы
./start.sh
# или
make up

# Тестирование
./test_api.sh
python3 example_usage.py

# Мониторинг
make logs
make status

# Остановка
make down

# Полная пересборка
make rebuild
```
### Скрины из Сваггера
![POST /parser/parse](img.png)

![GET parser/status/3f1f2a4b-b0a9-4e29-86b0-8d65f31b0a77](img_2.png)

![POST /queue/parse](img_1.png)

![GET /queue/status/585cfe15-69c9-4202-ad4c-059810d58741](img_3.png)