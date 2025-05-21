# Предложение обмена

Создаёт новую запись об обмене, учитывая также запись в ассоциативную таблицу

**URL** : `/exchange`

**Method** : `POST`

**Auth required** : NO

**Permissions required** : None

**Data constraints** : `{}`

```json
{
  "date": "2025-04-13T12:02:21.586Z",
  "status": "pending",
  "sender_id": 0,
  "receiver_id": 0,
  "items": [
    {
        "book_id": 0,
        "direction": "given"
    }
  ]
}
```

## Success Responses

**Code** : `200 OK`

**Content** : `{}`

```json
{
  "status": 0,
  "data": {
    "date": "2025-04-13T12:02:21.602Z",
    "status": "pending",
    "sender_id": 0,
    "receiver_id": 0,
    "id": 0
  }
}
```


# Чтение обмена

Получает запись об обмене, учитывая также запись в ассоциативную таблицу

**URL** : `/exchange`

**Method** : `GET`

**Auth required** : NO

**Permissions required** : None

**Data constraints** : `{}`

## Success Responses

**Code** : `200 OK`

**Content** : `{}`

```json
{
  "date": "2025-04-13T12:02:21.586Z",
  "status": "pending",
  "sender_id": 0,
  "receiver_id": 0,
  "id": 0,
  "items": [
    {
        "book_id": 0,
        "direction": "given"
    }
  ]
}
```