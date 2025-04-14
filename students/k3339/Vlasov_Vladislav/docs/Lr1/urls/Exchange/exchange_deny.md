# Отменить обмен

Меняет статус обмена на отменённый

**URL** : `/exchange/deny/{exchange_id}`

**Method** : `PATCH`

**Auth required** : NO

**Permissions required** : None

**Data constraints** : `{}`

## Success Responses

**Code** : `200 OK`

**Content** : `{}`

```json
{
  "status": 202,
  "message": "deny"
}
```