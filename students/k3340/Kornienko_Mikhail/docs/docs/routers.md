# Полная документация API роутеров системы хакатонов

Документ описывает все доступные роуты (эндпоинты), разделённые по сущностям.

---

## Users

### POST `/users/signup`
**Описание:** Регистрация нового пользователя.

**Request body:**
```json
{
  "username": "user123",
  "password": "secret"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "user123"
}
```

---

### POST `/users/signin`
**Описание:** Авторизация пользователя.

**Request body:**
```json
{
  "username": "user123",
  "password": "secret"
}
```

**Response:**
```json
{
  "id": 1,
  "access_token": "JWT_TOKEN"
}
```

---

### GET `/users/me`
**Описание:** Получение текущего пользователя (по токену).

**Headers:**
`Authorization: Bearer <token>`

**Response:** UserRead

---

### GET `/users/`
**Описание:** Получение списка всех пользователей.

**Response:** Список пользователей

---

### PATCH `/users/change_password`
**Описание:** Смена пароля текущего пользователя.

**Request body:**
```json
{
  "old_password": "old",
  "new_password": "new"
}
```

**Response:**
```json
{
  "msg": "Password changed successfully"
}
```

---

## Teams

### POST `/teams/`
**Описание:** Создание новой команды. Текущий пользователь становится лидером.

**Request body:**
```json
{
  "name": "Team A",
  "description": "Хорошая команда"
}
```

**Response:** Team

---

### POST `/teams/{team_id}/join`
**Описание:** Присоединение к команде.

**Response:** Объект команды

---

### DELETE `/teams/{team_id}/leave`
**Описание:** Покинуть команду.

**Response:** Объект команды

---

### GET `/teams/`
**Описание:** Получение списка команд.

**Response:** Список команд

---

### GET `/teams/{team_id}`
**Описание:** Получение команды по ID.

**Response:** TeamWithFullDetails

---

## Tasks

### POST `/tasks/`
**Описание:** Создание задачи (только для организаторов).

**Request body:**
```json
{
  "title": "AI Challenge",
  "description": "Build a model",
  "requirements": "Use PyTorch",
  "evaluation_criteria": "Accuracy"
}
```

**Response:** Task

---

### GET `/tasks/`
**Описание:** Список задач.

**Response:** Список объектов Task

---

### GET `/tasks/{task_id}`
**Описание:** Задача по ID.

**Response:** Task

---

## Submissions

### POST `/submissions/`
**Описание:** Загрузка решения команды по задаче.

**Request body:**
```json
{
  "description": "Our solution",
  "submission_url": "https://github.com/project",
  "team_id": 1,
  "task_id": 1
}
```

**Response:** Submission

---

### GET `/submissions/`
**Описание:** Список всех загрузок.

**Response:** Список Submission

---

### GET `/submissions/{submission_id}`
**Описание:** Получение конкретной загрузки.

**Response:** Submission

---

_Конец документации роутеров_