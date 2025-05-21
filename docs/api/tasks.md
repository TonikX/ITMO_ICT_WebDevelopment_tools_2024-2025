# API Задач

API задач позволяет создавать и управлять задачами в проектах.

## Получить список задач

Получить список всех задач.

**Конечная точка:** `GET /tasks`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Параметры запроса:**

```
skip: 0
limit: 100
project_id: 1 (опционально)
user_id: 1 (опционально)
status: in_progress (опционально)
```

**Ответ:**

```json
[
  {
    "id": 1,
    "title": "Разработка базы данных",
    "description": "Создание схемы базы данных для проекта",
    "status": "completed",
    "priority": "high",
    "due_date": "2024-05-20",
    "project_id": 1,
    "assigned_user_id": 1,
    "created_at": "2024-05-15T12:00:00"
  },
  {
    "id": 2,
    "title": "Разработка API",
    "description": "Создание REST API для проекта",
    "status": "in_progress",
    "priority": "high",
    "due_date": "2024-06-01",
    "project_id": 1,
    "assigned_user_id": 1,
    "created_at": "2024-05-15T12:05:00"
  }
]
```

## Создать новую задачу

Создать новую задачу в проекте.

**Конечная точка:** `POST /tasks`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Тело запроса:**

```json
{
  "title": "Разработка фронтенда",
  "description": "Создание пользовательского интерфейса для проекта",
  "status": "not_started",
  "priority": "medium",
  "due_date": "2024-07-01",
  "project_id": 1,
  "assigned_user_id": 3
}
```

**Ответ:**

```json
{
  "id": 3,
  "title": "Разработка фронтенда",
  "description": "Создание пользовательского интерфейса для проекта",
  "status": "not_started",
  "priority": "medium",
  "due_date": "2024-07-01",
  "project_id": 1,
  "assigned_user_id": 3,
  "created_at": "2024-05-17T14:20:00"
}
```

## Получить задачу по ID

Получить информацию о конкретной задаче по её ID.

**Конечная точка:** `GET /tasks/{task_id}`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ответ:**

```json
{
  "id": 1,
  "title": "Разработка базы данных",
  "description": "Создание схемы базы данных для проекта",
  "status": "completed",
  "priority": "high",
  "due_date": "2024-05-20",
  "project_id": 1,
  "assigned_user_id": 1,
  "created_at": "2024-05-15T12:00:00",
  "project": {
    "id": 1,
    "name": "Веб-приложение"
  },
  "assigned_user": {
    "id": 1,
    "username": "johndoe",
    "full_name": "Иван Иванов"
  }
}
```

## Обновить задачу

Обновить информацию о задаче.

**Конечная точка:** `PUT /tasks/{task_id}`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Тело запроса:**

```json
{
  "title": "Разработка схемы базы данных",
  "status": "completed",
  "priority": "high",
  "due_date": "2024-05-25"
}
```

**Ответ:**

```json
{
  "id": 1,
  "title": "Разработка схемы базы данных",
  "description": "Создание схемы базы данных для проекта",
  "status": "completed",
  "priority": "high",
  "due_date": "2024-05-25",
  "project_id": 1,
  "assigned_user_id": 1,
  "created_at": "2024-05-15T12:00:00"
}
```

## Удалить задачу

Удалить задачу из системы.

**Конечная точка:** `DELETE /tasks/{task_id}`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ответ:**

```json
{
  "message": "Задача успешно удалена"
}
```

## Назначить задачу пользователю

Назначить задачу пользователю.

**Конечная точка:** `PUT /tasks/{task_id}/assign`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Тело запроса:**

```json
{
  "user_id": 2
}
```

**Ответ:**

```json
{
  "message": "Задача успешно назначена пользователю",
  "task_id": 1,
  "user_id": 2
}
```

## Изменить статус задачи

Изменить статус задачи.

**Конечная точка:** `PUT /tasks/{task_id}/status`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Тело запроса:**

```json
{
  "status": "in_progress"
}
```

**Ответ:**

```json
{
  "message": "Статус задачи успешно изменен",
  "task_id": 1,
  "status": "in_progress"
}
```