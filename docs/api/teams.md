# API Команд

API команд позволяет создавать и управлять командами в системе.

## Получить список команд

Получить список всех команд.

**Конечная точка:** `GET /teams`

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
    "name": "Команда разработки",
    "description": "Команда, занимающаяся разработкой основного продукта",
    "created_at": "2024-05-15T12:00:00",
    "owner_id": 1,
    "member_count": 5
  },
  {
    "id": 2,
    "name": "Команда дизайна",
    "description": "Команда, занимающаяся дизайном пользовательского интерфейса",
    "created_at": "2024-05-16T10:30:00",
    "owner_id": 2,
    "member_count": 3
  }
]
```

## Создать новую команду

Создать новую команду.

**Конечная точка:** `POST /teams`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Тело запроса:**

```json
{
  "name": "Команда тестирования",
  "description": "Команда, занимающаяся тестированием продукта"
}
```

**Ответ:**

```json
{
  "id": 3,
  "name": "Команда тестирования",
  "description": "Команда, занимающаяся тестированием продукта",
  "created_at": "2024-05-17T14:20:00",
  "owner_id": 1,
  "member_count": 1
}
```

## Получить команду по ID

Получить информацию о конкретной команде по её ID.

**Конечная точка:** `GET /teams/{team_id}`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ответ:**

```json
{
  "id": 1,
  "name": "Команда разработки",
  "description": "Команда, занимающаяся разработкой основного продукта",
  "created_at": "2024-05-15T12:00:00",
  "owner_id": 1,
  "members": [
    {
      "id": 1,
      "username": "johndoe",
      "full_name": "Иван Иванов",
      "role": "owner"
    },
    {
      "id": 3,
      "username": "alexsmith",
      "full_name": "Алексей Кузнецов",
      "role": "member"
    }
  ],
  "projects": [
    {
      "id": 1,
      "name": "Веб-приложение",
      "status": "in_progress"
    }
  ]
}
```

## Обновить команду

Обновить информацию о команде.

**Конечная точка:** `PUT /teams/{team_id}`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Тело запроса:**

```json
{
  "name": "Команда разработки бэкенда",
  "description": "Команда, занимающаяся разработкой серверной части приложения"
}
```

**Ответ:**

```json
{
  "id": 1,
  "name": "Команда разработки бэкенда",
  "description": "Команда, занимающаяся разработкой серверной части приложения",
  "created_at": "2024-05-15T12:00:00",
  "owner_id": 1,
  "member_count": 5
}
```

## Удалить команду

Удалить команду из системы.

**Конечная точка:** `DELETE /teams/{team_id}`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ответ:**

```json
{
  "message": "Команда успешно удалена"
}
```

## Добавить пользователя в команду

Добавить пользователя в команду.

**Конечная точка:** `POST /teams/{team_id}/members`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Тело запроса:**

```json
{
  "user_id": 4,
  "role": "member"
}
```

**Ответ:**

```json
{
  "message": "Пользователь успешно добавлен в команду",
  "team_id": 1,
  "user_id": 4,
  "role": "member"
}
```

## Удалить пользователя из команды

Удалить пользователя из команды.

**Конечная точка:** `DELETE /teams/{team_id}/members/{user_id}`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ответ:**

```json
{
  "message": "Пользователь успешно удален из команды"
}
```