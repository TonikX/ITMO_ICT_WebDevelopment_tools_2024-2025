# Показать книгу

Выводит информацию о конкретной книге

**URL** : `/book/{book_id}`

**Method** : `GET`

**Auth required** : NO

**Permissions required** : None

**Data constraints** : `{}`

## Success Responses

**Code** : `200 OK`

**Content** : `{}`

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
  "status": "available",
  "id": 0
}
```

# Изменить книгу

Изменяет информацию о конкретной книге


**Method** : `PATCH`

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
```