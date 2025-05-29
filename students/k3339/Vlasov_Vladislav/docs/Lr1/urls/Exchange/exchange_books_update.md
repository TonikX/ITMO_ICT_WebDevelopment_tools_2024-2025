# Изменить книги в обмене

Удаляет и добавляет записи из таблицы ассоциации для конкретного обмена

**URL** : `/exchange_receiver_list/{receiver_id}`

**Method** : `PUT`

**Auth required** : NO

**Permissions required** : None

**Data constraints** : `{[{}]}`

```json
{
  "deleted_books": [
        {
            "book_id": 0,
            "direction": "given"
        }
  ],
  "new_books": [
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
  "date": "2025-04-13T12:11:43.830Z",
  "status": "pending",
  "sender_id": 0,
  "receiver_id": 0,
  "id": 0
}
```