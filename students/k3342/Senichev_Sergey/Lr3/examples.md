# Примеры использования API

## Тестирование Task Management API

### 1. Создание спринта
```bash
curl -X POST "http://localhost:8000/sprints/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sprint 1 - Authentication",
    "start_at": "2024-01-01T00:00:00",
    "end_at": "2024-01-31T23:59:59"
  }'
```

Ответ:
```json
{
  "status": 200,
  "data": {
    "id": 1,
    "title": "Sprint 1 - Authentication",
    "start_at": "2024-01-01T00:00:00",
    "end_at": "2024-01-31T23:59:59",
    "tasks": []
  }
}
```

### 2. Создание задачи
```bash
curl -X POST "http://localhost:8000/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Implement user login",
    "priority": "major",
    "description": "Create login endpoint with JWT authentication",
    "planned_end_at": "2024-01-15T12:00:00",
    "status": "open",
    "sprint_id": 1
  }'
```

Ответ:
```json
{
  "status": 200,
  "data": {
    "id": 1,
    "summary": "Implement user login",
    "priority": "major",
    "description": "Create login endpoint with JWT authentication",
    "planned_end_at": "2024-01-15T12:00:00",
    "status": "open",
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:00:00",
    "sprint": {
      "id": 1,
      "title": "Sprint 1 - Authentication",
      "start_at": "2024-01-01T00:00:00",
      "end_at": "2024-01-31T23:59:59"
    }
  }
}
```

### 3. Получение всех задач
```bash
curl -X GET "http://localhost:8000/tasks/"
```

### 4. Обновление задачи
```bash
curl -X PATCH "http://localhost:8000/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Implement user login with 2FA",
    "priority": "critical",
    "description": "Create login endpoint with JWT authentication and two-factor authentication",
    "planned_end_at": "2024-01-20T12:00:00",
    "status": "in_progress",
    "sprint_id": 1
  }'
```

## Тестирование Parser API

### 1. Синхронный парсинг одного репозитория
```bash
curl -X POST "http://localhost:8001/parse" \
  -H "Content-Type: application/json" \
  -d '{
    "repositories": ["python/cpython"]
  }'
```

Ответ:
```json
{
  "message": "Parsing completed successfully",
  "status": "completed",
  "duration": 3.45,
  "tasks_parsed": 10,
  "errors": [],
  "repositories": ["python/cpython"]
}
```

### 2. Синхронный парсинг нескольких репозиториев
```bash
curl -X POST "http://localhost:8001/parse" \
  -H "Content-Type: application/json" \
  -d '{
    "repositories": ["python/cpython", "django/django"]
  }'
```

### 3. Асинхронный парсинг
```bash
# Запуск задачи
curl -X POST "http://localhost:8001/parse/async" \
  -H "Content-Type: application/json" \
  -d '{
    "repositories": ["python/cpython", "django/django", "pallets/flask"]
  }'
```

Ответ:
```json
{
  "message": "Parsing task queued successfully",
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "repositories": ["python/cpython", "django/django", "pallets/flask"]
}
```

### 4. Проверка статуса асинхронной задачи
```bash
curl -X GET "http://localhost:8001/task/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

Возможные ответы:

**Задача в процессе:**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "PROGRESS",
  "result": {
    "current": 1,
    "total": 3,
    "status": "Parsing python/cpython..."
  }
}
```

**Задача завершена успешно:**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "SUCCESS",
  "result": {
    "status": "SUCCESS",
    "result": {
      "status": "completed",
      "duration": 15.67,
      "tasks_parsed": 30,
      "errors": [],
      "repositories": ["python/cpython", "django/django", "pallets/flask"]
    }
  }
}
```

**Задача завершена с ошибкой:**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "FAILURE",
  "error": "GitHub API rate limit exceeded"
}
```

## Тестирование интеграции

### 1. Вызов парсера из основного приложения (синхронно)
```bash
curl -X POST "http://localhost:8000/parse" \
  -H "Content-Type: application/json" \
  -d '{
    "repositories": ["python/cpython"]
  }'
```

Ответ:
```json
{
  "message": "Parsing completed successfully",
  "repositories": ["python/cpython"]
}
```

### 2. Вызов парсера из основного приложения (асинхронно)
```bash
curl -X POST "http://localhost:8000/parse/async" \
  -H "Content-Type: application/json" \
  -d '{
    "repositories": ["django/django", "pallets/flask"]
  }'
```

Ответ:
```json
{
  "message": "Parsing task queued successfully",
  "task_id": "b2c3d4e5-f6g7-8901-bcde-f23456789012",
  "repositories": ["django/django", "pallets/flask"]
}
```

## Проверка состояния сервисов

### 1. Проверка основного приложения
```bash
curl -X GET "http://localhost:8000/health"
```

Ответ:
```json
{
  "status": "healthy",
  "service": "task-management-api"
}
```

### 2. Проверка парсера
```bash
curl -X GET "http://localhost:8001/health"
```

Ответ:
```json
{
  "status": "healthy",
  "service": "github-parser-api"
}
```

### 3. Информация об API
```bash
# Основное приложение
curl -X GET "http://localhost:8000/"

# Парсер
curl -X GET "http://localhost:8001/"
```

## Примеры ошибок и их обработка

### 1. Ошибка валидации данных
```bash
curl -X POST "http://localhost:8000/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "",
    "priority": "invalid_priority",
    "status": "open"
  }'
```

Ответ:
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "summary"],
      "msg": "String should have at least 1 character"
    },
    {
      "type": "enum",
      "loc": ["body", "priority"],
      "msg": "Input should be 'trivial', 'minor', 'major', 'critical' or 'blocker'"
    }
  ]
}
```

### 2. Ошибка парсера (недоступный репозиторий)
```bash
curl -X POST "http://localhost:8001/parse" \
  -H "Content-Type: application/json" \
  -d '{
    "repositories": ["nonexistent/repository"]
  }'
```

Ответ:
```json
{
  "message": "Parsing completed successfully",
  "status": "completed",
  "duration": 1.23,
  "tasks_parsed": 0,
  "errors": [
    "Error parsing nonexistent/repository: 404 Client Error: Not Found"
  ],
  "repositories": ["nonexistent/repository"]
}
```

### 3. Ошибка сервиса недоступен
```bash
# Если парсер недоступен
curl -X POST "http://localhost:8000/parse" \
  -H "Content-Type: application/json" \
  -d '{
    "repositories": ["python/cpython"]
  }'
```

Ответ:
```json
{
  "detail": "Parser service error: HTTPConnectionPool(host='parser', port=8001): Max retries exceeded"
}
```

## Полный workflow тестирования

### Скрипт для комплексного тестирования
```bash
#!/bin/bash

echo "=== Comprehensive API Testing ==="

# 1. Проверка здоровья сервисов
echo "1. Health checks..."
curl -s http://localhost:8000/health | jq .
curl -s http://localhost:8001/health | jq .

# 2. Создание спринта
echo "2. Creating sprint..."
SPRINT_RESPONSE=$(curl -s -X POST "http://localhost:8000/sprints/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Sprint",
    "start_at": "2024-01-01T00:00:00",
    "end_at": "2024-01-31T23:59:59"
  }')
echo $SPRINT_RESPONSE | jq .
SPRINT_ID=$(echo $SPRINT_RESPONSE | jq -r '.data.id')

# 3. Создание задачи
echo "3. Creating task..."
TASK_RESPONSE=$(curl -s -X POST "http://localhost:8000/tasks/" \
  -H "Content-Type: application/json" \
  -d "{
    \"summary\": \"Test Task\",
    \"priority\": \"major\",
    \"description\": \"Test task description\",
    \"planned_end_at\": \"2024-01-15T12:00:00\",
    \"status\": \"open\",
    \"sprint_id\": $SPRINT_ID
  }")
echo $TASK_RESPONSE | jq .

# 4. Синхронный парсинг
echo "4. Synchronous parsing..."
curl -s -X POST "http://localhost:8001/parse" \
  -H "Content-Type: application/json" \
  -d '{"repositories": ["python/cpython"]}' | jq .

# 5. Асинхронный парсинг
echo "5. Asynchronous parsing..."
ASYNC_RESPONSE=$(curl -s -X POST "http://localhost:8001/parse/async" \
  -H "Content-Type: application/json" \
  -d '{"repositories": ["django/django"]}')
echo $ASYNC_RESPONSE | jq .
TASK_ID=$(echo $ASYNC_RESPONSE | jq -r '.task_id')

# 6. Проверка статуса асинхронной задачи
echo "6. Checking async task status..."
sleep 5
curl -s "http://localhost:8001/task/$TASK_ID" | jq .

# 7. Интеграционный тест
echo "7. Integration test..."
curl -s -X POST "http://localhost:8000/parse" \
  -H "Content-Type: application/json" \
  -d '{"repositories": ["pallets/flask"]}' | jq .

echo "=== Testing completed ==="
```

Сохраните этот скрипт как `test_all.sh` и запустите:
```bash
chmod +x test_all.sh
./test_all.sh
``` 