# Показать профиль

Выводит информацию о конкретном профиле

**URL** : `/profile/{profile_id}`

**Method** : `GET`

**Auth required** : NO

**Permissions required** : None

**Data constraints** : `{}`

## Success Responses

**Code** : `200 OK`

**Content** : `{}`

```json
{
  "full_name": "",
  "city": "",
  "about": "",
  "account_id": 0,
  "id": 0
}
```

# Изменить профиль

Изменяет информацию о конкретном профиле


**Method** : `PATCH`

**Auth required** : YES

**Permissions required** : None

**Data constraints** : `{}`

```json
{
  "full_name": "string",
  "city": "string",
  "about": "string"
}
```

## Success Responses

**Code** : `200 OK`

**Content** : `{}`

```json
{
  "full_name": "",
  "city": "",
  "about": "",
  "account_id": 0,
  "id": 0
}
```