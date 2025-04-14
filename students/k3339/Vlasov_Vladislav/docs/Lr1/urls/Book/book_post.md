# Создание новой книги

Создаёт новую запись о книге

**URL** : `/book`

**Method** : `POST`

**Auth required** : NO

**Permissions required** : None

**Data constraints** : `{}`

```json
{
  "owner_id": 0,
  "title": "string",
  "author": "string",
  "year": 0,
  "condition": "good",
  "genre": "string",
  "language": "string",
  "description": "string",
  "status": "available"
}
```

## Success Responses

**Code** : `200 OK`

**Content** : `{}`

```json
{
  "status": 201,
  "data": {
    "owner_id": 0,
    "title": "string",
    "author": "string",
    "year": 0,
    "condition": "good",
    "genre": "string",
    "language": "string",
    "description": "string",
    "status": "available",
    "id": 0
  }
}
```