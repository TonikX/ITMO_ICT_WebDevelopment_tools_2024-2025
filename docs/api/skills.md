# API Навыков

API навыков позволяет управлять навыками пользователей в системе.

## Получить список навыков

Получить список всех навыков.

**Конечная точка:** `GET /skills`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Параметры запроса:**

```
skip: 0
limit: 100
```

**Ответ:**

```json
[
  {
    "id": 1,
    "name": "Python",
    "category": "programming",
    "created_at": "2024-05-15T12:00:00"
  },
  {
    "id": 2,
    "name": "FastAPI",
    "category": "framework",
    "created_at": "2024-05-15T12:05:00"
  },
  {
    "id": 3,
    "name": "PostgreSQL",
    "category": "database",
    "created_at": "2024-05-15T12:10:00"
  }
]
```

## Создать новый навык

Создать новый навык в системе.

**Конечная точка:** `POST /skills`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Тело запроса:**

```json
{
  "name": "Docker",
  "category": "devops",
  "description": "Платформа для разработки, доставки и запуска приложений в контейнерах"
}
```

**Ответ:**

```json
{
  "id": 4,
  "name": "Docker",
  "category": "devops",
  "description": "Платформа для разработки, доставки и запуска приложений в контейнерах",
  "created_at": "2024-05-17T14:20:00"
}
```

## Получить навык по ID

Получить информацию о конкретном навыке по его ID.

**Конечная точка:** `GET /skills/{skill_id}`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ответ:**

```json
{
  "id": 1,
  "name": "Python",
  "category": "programming",
  "description": "Высокоуровневый язык программирования общего назначения",
  "created_at": "2024-05-15T12:00:00",
  "users": [
    {
      "id": 1,
      "username": "johndoe",
      "level": "expert"
    },
    {
      "id": 3,
      "username": "alexsmith",
      "level": "intermediate"
    }
  ]
}
```

## Обновить навык

Обновить информацию о навыке.

**Конечная точка:** `PUT /skills/{skill_id}`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Тело запроса:**

```json
{
  "name": "Python 3",
  "description": "Высокоуровневый язык программирования общего назначения с акцентом на читаемость кода"
}
```

**Ответ:**

```json
{
  "id": 1,
  "name": "Python 3",
  "category": "programming",
  "description": "Высокоуровневый язык программирования общего назначения с акцентом на читаемость кода",
  "created_at": "2024-05-15T12:00:00"
}
```

## Удалить навык

Удалить навык из системы.

**Конечная точка:** `DELETE /skills/{skill_id}`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ответ:**

```json
{
  "message": "Навык успешно удален"
}
```

## Добавить навык пользователю

Добавить навык пользователю с указанием уровня владения.

**Конечная точка:** `POST /users/{user_id}/skills`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Тело запроса:**

```json
{
  "skill_id": 1,
  "level": "expert"
}
```

**Ответ:**

```json
{
  "message": "Навык успешно добавлен пользователю",
  "user_id": 1,
  "skill_id": 1,
  "level": "expert"
}
```

## Обновить уровень навыка пользователя

Обновить уровень владения навыком для пользователя.

**Конечная точка:** `PUT /users/{user_id}/skills/{skill_id}`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Тело запроса:**

```json
{
  "level": "advanced"
}
```

**Ответ:**

```json
{
  "message": "Уровень навыка успешно обновлен",
  "user_id": 1,
  "skill_id": 1,
  "level": "advanced"
}
```

## Удалить навык у пользователя

Удалить навык у пользователя.

**Конечная точка:** `DELETE /users/{user_id}/skills/{skill_id}`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ответ:**

```json
{
  "message": "Навык успешно удален у пользователя"
}
```
