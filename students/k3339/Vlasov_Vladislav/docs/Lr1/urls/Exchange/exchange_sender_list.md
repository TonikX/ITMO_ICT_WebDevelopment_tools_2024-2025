# Показать отправленные обмены

Выводит информацию обо всех отправленных обменах пользователя, только в состоянии pending

**URL** : `/exchange_sender_list/{sender_id}`

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
]
```