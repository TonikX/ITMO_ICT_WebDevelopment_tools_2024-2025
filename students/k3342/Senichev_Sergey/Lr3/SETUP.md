# Инструкция по настройке и запуску

## Предварительные требования

1. **Docker** и **Docker Compose** должны быть установлены
2. **Python 3.11+** для запуска тестов (опционально)
3. **Make** для использования Makefile команд (опционально)

## Запуск

### 1. Запуск всех сервисов
```bash
make up-build
# или напрямую
docker-compose up -d --build
```

### 2. Проверка статуса сервисов
```bash
make status
# или напрямую
docker-compose ps
```

### 3. Тестирование API
```bash
make test
# или ручное тестирование эндпоинтов
make test-endpoints
```

## Доступные сервисы

- **Task Management API**: http://localhost:8000
  - Swagger UI: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc

- **Parser API**: http://localhost:8001
  - Swagger UI: http://localhost:8001/docs
  - ReDoc: http://localhost:8001/redoc

- **PostgreSQL**: localhost:5432
  - База данных: lab_db
  - Пользователь: ***
  - Пароль: ***

- **Redis**: localhost:6379

## Основные команды

### Управление сервисами
```bash
make up          # Запустить сервисы
make down        # Остановить сервисы
make restart     # Перезапустить сервисы
make logs        # Показать логи всех сервисов
make clean       # Очистить Docker ресурсы
```

### Логи отдельных сервисов
```bash
make logs-app      # Логи FastAPI приложения
make logs-parser   # Логи парсера
make logs-celery   # Логи Celery воркера
```

### Подключение к контейнерам
```bash
make shell-app     # Подключиться к контейнеру приложения
make shell-parser  # Подключиться к контейнеру парсера
make db-shell      # Подключиться к PostgreSQL
make redis-cli     # Подключиться к Redis
```

## Тестирование функциональности

### 1. Тестирование Task Management API

#### Создание спринта
```bash
curl -X POST "http://localhost:8000/sprints/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sprint 1",
    "start_at": "2024-01-01T00:00:00",
    "end_at": "2024-01-31T23:59:59"
  }'
```

#### Создание задачи
```bash
curl -X POST "http://localhost:8000/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Test Task",
    "priority": "major",
    "description": "Test task description",
    "planned_end_at": "2024-01-15T12:00:00",
    "status": "open",
    "sprint_id": 1
  }'
```

### 2. Тестирование Parser API

#### Синхронный парсинг
```bash
curl -X POST "http://localhost:8001/parse" \
  -H "Content-Type: application/json" \
  -d '{
    "repositories": ["python/cpython"]
  }'
```

#### Асинхронный парсинг
```bash
# Запуск задачи
curl -X POST "http://localhost:8001/parse/async" \
  -H "Content-Type: application/json" \
  -d '{
    "repositories": ["django/django"]
  }'

# Проверка статуса задачи (замените TASK_ID на полученный ID)
curl -X GET "http://localhost:8001/task/TASK_ID"
```

### 3. Тестирование интеграции

#### Вызов парсера из основного приложения
```bash
# Синхронный вызов
curl -X POST "http://localhost:8000/parse" \
  -H "Content-Type: application/json" \
  -d '{
    "repositories": ["python/cpython"]
  }'

# Асинхронный вызов
curl -X POST "http://localhost:8000/parse/async" \
  -H "Content-Type: application/json" \
  -d '{
    "repositories": ["django/django"]
  }'
```

## Мониторинг и отладка

### Просмотр логов
```bash
# Все логи
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f app
docker-compose logs -f parser
docker-compose logs -f celery-worker
```

### Проверка состояния Celery
```bash
# Подключение к Redis для просмотра очередей
make redis-cli
# В Redis CLI:
# KEYS *
# LLEN celery
```

### Проверка базы данных
```bash
# Подключение к PostgreSQL
make db-shell
# В psql:
# \dt - список таблиц
# SELECT * FROM task; - просмотр задач
# SELECT * FROM parsed_task; - просмотр распарсенных задач
```

## Решение проблем

### Проблема: Сервисы не запускаются
```bash
# Проверьте логи
make logs

# Пересоберите образы
make clean
make up-build
```

### Проблема: Ошибки подключения к базе данных
```bash
# Проверьте статус PostgreSQL
docker-compose ps postgres

# Проверьте логи PostgreSQL
docker-compose logs postgres
```

### Проблема: Celery задачи не выполняются
```bash
# Проверьте статус Redis
docker-compose ps redis

# Проверьте логи Celery воркера
make logs-celery

# Проверьте очереди в Redis
make redis-cli
```

### Проблема: GitHub API rate limit
```bash
# Установите GITHUB_TOKEN в .env файле
echo "GITHUB_TOKEN=your_github_token_here" >> .env

# Перезапустите сервисы
make restart
```

## Остановка и очистка

```bash
# Остановка сервисов
make down

# Полная очистка (включая volumes)
make clean
``` 