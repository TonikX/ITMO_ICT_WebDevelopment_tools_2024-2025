# Показать аккаунт

Выводит информацию о конкретном аккаунте (с профилем)

**URL** : `/account/{account_id}`

**Method** : `GET`

**Auth required** : NO

**Permissions required** : None

**Data constraints** : `{}`

## Success Responses

**Code** : `200 OK`

**Content** : `{}`

```json
{
  "login": "string",
  "password": "string",
  "email": "string",
  "profile": {
    "full_name": "",
    "city": "",
    "about": "",
    "account_id": 0,
    "id": 0
  }
}
```

# Изменить аккаунт

Изменяет информацию о конкретном аккаунте


**Method** : `PATCH`

**Auth required** : YES

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
  "login": "string",
  "password": "string",
  "email": "string",
  "id": 0
}
```