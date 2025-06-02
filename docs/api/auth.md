# API Аутентификации

API аутентификации позволяет пользователям регистрироваться, входить в систему и управлять своими учетными записями.

## Регистрация пользователя

Регистрация нового пользователя в системе.

**Конечная точка:** `POST /auth/register`

**Тело запроса:**

```json
{
  "username": "johndoe",
  "email": "john.doe@example.com",
  "full_name": "Иван Иванов",
  "password": "securepassword123",
  "bio": "Разработчик с опытом работы в веб-технологиях",
  "years_of_experience": 3.5
}
```

**Ответ:**

```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john.doe@example.com",
  "full_name": "Иван Иванов",
  "bio": "Разработчик с опытом работы в веб-технологиях",
  "years_of_experience": 3.5,
  "is_active": true,
  "created_at": "2024-05-15T12:00:00"
}
```

## Вход в систему

Аутентификация пользователя и получение JWT токена.

**Конечная точка:** `POST /auth/login`

**Тело запроса:**

```json
{
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Ответ:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Получение информации о текущем пользователе

Получение информации о текущем аутентифицированном пользователе.

**Конечная точка:** `GET /auth/me`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ответ:**

```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john.doe@example.com",
  "full_name": "Иван Иванов",
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

## Изменение пароля

Изменение пароля текущего пользователя.

**Конечная точка:** `PUT /auth/password`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Тело запроса:**

```json
{
  "current_password": "securepassword123",
  "new_password": "evenmoresecurepassword456"
}
```

**Ответ:**

```json
{
  "message": "Пароль успешно изменен"
}
```

## Деактивация учетной записи

Деактивация учетной записи текущего пользователя.

**Конечная точка:** `DELETE /auth/me`

**Заголовки:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ответ:**

```json
{
  "message": "Учетная запись успешно деактивирована"
}
```

## Обновление профиля

Обновление информации профиля текущего пользователя.

**Конечная точка:** `PUT /auth/me`

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
  "email": "john.doe@example.com",
  "full_name": "Иван Петрович Иванов",
  "bio": "Старший разработчик с опытом работы в веб-технологиях и машинном обучении",
  "years_of_experience": 4.5,
  "is_active": true,
  "created_at": "2024-05-15T12:00:00"
}
```

## Технические детали

### JWT токены

API использует JWT (JSON Web Tokens) для аутентификации. Токен содержит информацию о пользователе и имеет ограниченный срок действия (по умолчанию 30 минут).

Структура JWT токена:

- **Header**: Содержит тип токена и используемый алгоритм шифрования
- **Payload**: Содержит данные о пользователе (sub - идентификатор пользователя)
- **Signature**: Подпись, гарантирующая целостность токена

### Безопасность паролей

Пароли хранятся в базе данных в хешированном виде с использованием библиотеки bcrypt. Это обеспечивает безопасность даже в случае утечки базы данных.

### Обработка ошибок

API возвращает следующие коды ошибок:

- **401 Unauthorized**: Неверные учетные данные или отсутствие токена
- **403 Forbidden**: Недостаточно прав для выполнения операции
- **422 Unprocessable Entity**: Неверный формат данных
