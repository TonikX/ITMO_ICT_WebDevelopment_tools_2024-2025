# API Пользователей

API пользователей позволяет управлять пользователями в системе.

## Получить список пользователей

Получить список всех пользователей.

**Конечная точка:** `GET /users`

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
    "username": "johndoe",
    "full_name": "Иван Иванов",
    "email": "john.doe@example.com",
    "bio": "Разработчик с опытом работы в веб-технологиях",
    "years_of_experience": 3.5,
    "is_active": true,
    "created_at": "2024-05-15T12:00:00"
  },
  {
    "id": 2,
    "username": "janedoe",
    "full_name": "Мария Петрова",
    "email": "jane.doe@example.com",
    "bio": "Дизайнер интерфейсов",
    "years_of_experience": 2.0,
    "is_active": true,
    "created_at": "2024-05-15T12:05:00"
  }
]
```

## Получить пользователя по ID

Получить информацию о конкретном пользователе по его ID.

**Конечная точка:** `GET /users/{user_id}`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ответ:**

```json
{
  "id": 1,
  "username": "johndoe",
  "full_name": "Иван Иванов",
  "email": "john.doe@example.com",
  "bio": "Разработчик с опытом работы в веб-технологиях",
  "years_of_experience": 3.5,
  "is_active": true,
  "created_at": "2024-05-15T12:00:00",
  "skills": [
    {
      "id": 1,
      "name": "Python",
      "level": "expert"
    },
    {
      "id": 2,
      "name": "FastAPI",
      "level": "intermediate"
    }
  ],
  "teams": [
    {
      "id": 1,
      "name": "Команда разработки",
      "role": "leader"
    }
  ]
}
```

## Обновить пользователя

Обновить информацию о пользователе (только для администраторов или самого пользователя).

**Конечная точка:** `PUT /users/{user_id}`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Тело запроса:**

```json
{
  "full_name": "Иван Петрович Иванов",
  "bio": "Старший разработчик с опытом работы в веб-технологиях и машинном обучении",
  "years_of_experience": 4.5
}
```

**Ответ:**

```json
{
  "id": 1,
  "username": "johndoe",
  "full_name": "Иван Петрович Иванов",
  "email": "john.doe@example.com",
  "bio": "Старший разработчик с опытом работы в веб-технологиях и машинном обучении",
  "years_of_experience": 4.5,
  "is_active": true,
  "created_at": "2024-05-15T12:00:00"
}
```

## Деактивировать пользователя

Деактивировать пользователя (только для администраторов).

**Конечная точка:** `DELETE /users/{user_id}`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ответ:**

```json
{
  "message": "Пользователь успешно деактивирован"
}
```

## Получить навыки пользователя

Получить список навыков пользователя.

**Конечная точка:** `GET /users/{user_id}/skills`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ответ:**

```json
[
  {
    "id": 1,
    "name": "Python",
    "category": "programming",
    "description": "Высокоуровневый язык программирования общего назначения",
    "level": "expert"
  },
  {
    "id": 2,
    "name": "FastAPI",
    "category": "framework",
    "description": "Современный, быстрый веб-фреймворк для создания API с Python",
    "level": "intermediate"
  }
]
```

## Получить команды пользователя

Получить список команд, в которых состоит пользователь.

**Конечная точка:** `GET /users/{user_id}/teams`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ответ:**

```json
[
  {
    "id": 1,
    "name": "Команда разработки",
    "description": "Команда разработчиков веб-приложений",
    "role": "leader",
    "created_at": "2024-05-15T12:00:00"
  },
  {
    "id": 2,
    "name": "Команда тестирования",
    "description": "Команда тестировщиков",
    "role": "member",
    "created_at": "2024-05-15T12:05:00"
  }
]
```

## Получить задачи пользователя

Получить список задач, назначенных пользователю.

**Конечная точка:** `GET /users/{user_id}/tasks`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Параметры запроса:**

```
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
    "project": {
      "id": 1,
      "title": "Веб-приложение"
    },
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
    "project": {
      "id": 1,
      "title": "Веб-приложение"
    },
    "created_at": "2024-05-15T12:05:00"
  }
]
```

## Поиск пользователей по навыкам

Найти пользователей, обладающих определенными навыками.

**Конечная точка:** `GET /users/search`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Параметры запроса:**

```
skills: 1,2,3
min_level: intermediate
```

**Ответ:**

```json
[
  {
    "id": 1,
    "username": "johndoe",
    "full_name": "Иван Иванов",
    "email": "john.doe@example.com",
    "bio": "Разработчик с опытом работы в веб-технологиях",
    "years_of_experience": 3.5,
    "is_active": true,
    "created_at": "2024-05-15T12:00:00",
    "matching_skills": [
      {
        "id": 1,
        "name": "Python",
        "level": "expert"
      },
      {
        "id": 2,
        "name": "FastAPI",
        "level": "intermediate"
      }
    ]
  }
]
```
