# Подтвердить обмен

Меняет статус обмена на подтверждённый, меняет владельцев книг и меняет статус записей, в которых участвуют те же книги, что и в текущем обмене на "отменён"

**URL** : `/exchange/accept/{exchange_id}`

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
  "message": "accept"
}
```