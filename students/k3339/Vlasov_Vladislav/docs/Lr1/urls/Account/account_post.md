# Создание нового аккаунта

Создаёт новый аккаунт

**URL** : `/account`

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
  "status": 201,
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