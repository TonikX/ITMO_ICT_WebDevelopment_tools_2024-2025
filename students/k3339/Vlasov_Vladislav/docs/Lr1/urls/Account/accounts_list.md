# Показать все аккаунты

Выводит информацию обо всех аккаутах

**URL** : `/account_list/`

**Method** : `GET`

**Auth required** : NO

**Permissions required** : None

**Data constraints** : `{}`

## Success Responses

**Code** : `200 OK`

**Content** : `[{}]`

```json
[
  {
    "login": "string",
    "password": "string",
    "email": "string",
    "id": 0
  }
]
```