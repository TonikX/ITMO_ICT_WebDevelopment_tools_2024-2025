# Аутентификация

Проверяет токен и возвращает пользователя

**URL** : `/account/authentication`

**Method** : `POST`

**Auth required** : NO

**Permissions required** : None

**Data constraints** : `{}`

## Success Responses

**Code** : `200 OK`

**Content** : `{}`

```json
{
  "status": 200,
  "data": {
    "login": "string",
    "password": "string",
    "email": "string",
    "id": 0
  }
}
```