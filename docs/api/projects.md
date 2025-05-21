# API Проектов

API проектов позволяет создавать и управлять проектами в системе.

## Получить список проектов

Получить список всех проектов.

**Конечная точка:** `GET /projects`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Параметры запроса:**

```
skip: 0
limit: 100
team_id: 1 (опционально)
```

**Ответ:**

```json
[
  {
    "id": 1,
    "name": "Веб-приложение",
    "description": "Разработка веб-приложения для управления задачами",
    "status": "in_progress",
    "start_date": "2024-05-15",
    "end_date": "2024-08-15",
    "team_id": 1,
    "created_at": "2024-05-15T12:00:00"
  },
  {
    "id": 2,
    "name": "Мобильное приложение",
    "description": "Разработка мобильного приложения для iOS и Android",
    "status": "planning",
    "start_date": "2024-06-01",
    "end_date": "2024-10-01",
    "team_id": 1,
    "created_at": "2024-05-16T10:30:00"
  }
]
```

## Создать новый проект

Создать новый проект.

**Конечная точка:** `POST /projects`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Тело запроса:**

```json
{
  "name": "API сервис",
  "description": "Разработка API сервиса для интеграции с внешними системами",
  "status": "planning",
  "start_date": "2024-06-15",
  "end_date": "2024-09-15",
  "team_id": 1
}
```

**Ответ:**

```json
{
  "id": 3,
  "name": "API сервис",
  "description": "Разработка API сервиса для интеграции с внешними системами",
  "status": "planning",
  "start_date": "2024-06-15",
  "end_date": "2024-09-15",
  "team_id": 1,
  "created_at": "2024-05-17T14:20:00"
}
```

## Получить проект по ID

Получить информацию о конкретном проекте по его ID.

**Конечная точка:** `GET /projects/{project_id}`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ответ:**

```json
{
  "id": 1,
  "name": "Веб-приложение",
  "description": "Разработка веб-приложения для управления задачами",
  "status": "in_progress",
  "start_date": "2024-05-15",
  "end_date": "2024-08-15",
  "team_id": 1,
  "created_at": "2024-05-15T12:00:00",
  "team": {
    "id": 1,
    "name": "Команда разработки"
  },
  "tasks": [
    {
      "id": 1,
      "title": "Разработка базы данных",
      "status": "completed"
    },
    {
      "id": 2,
      "title": "Разработка API",
      "status": "in_progress"
    }
  ]
}
```

## Обновить проект

Обновить информацию о проекте.

**Конечная точка:** `PUT /projects/{project_id}`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Тело запроса:**

```json
{
  "name": "Веб-приложение v2",
  "description": "Обновленная версия веб-приложения для управления задачами",
  "status": "in_progress",
  "end_date": "2024-09-15"
}
```

**Ответ:**

```json
{
  "id": 1,
  "name": "Веб-приложение v2",
  "description": "Обновленная версия веб-приложения для управления задачами",
  "status": "in_progress",
  "start_date": "2024-05-15",
  "end_date": "2024-09-15",
  "team_id": 1,
  "created_at": "2024-05-15T12:00:00"
}
```

## Удалить проект

Удалить проект из системы.

**Конечная точка:** `DELETE /projects/{project_id}`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ответ:**

```json
{
  "message": "Проект успешно удален"
}
```