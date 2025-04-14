# Авторизация

Проверяет логин и пароль, возвращает токен

**URL** : `/account/sing_in`

**Method** : `POST`

**Auth required** : NO

**Permissions required** : None

**Data constraints** : `{}`

```json
{
  "login": "string",
  "password": "string",
  "email": "string"
}
```

## Success Responses

**Code** : `200 OK`

**Content** : `{}`

```json
{
  "status": 200,
  "data": {
        "token": "string",
        "account": {
            "login": "string",
            "password": "string",
            "email": "string",
            "id": 0
        }
    } 
}
```