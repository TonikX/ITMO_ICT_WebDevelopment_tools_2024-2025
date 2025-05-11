## **URL**: ```/book_instance/{id} ```
### Назначение: Получение запроса на обмен по id
### **Method**: ```GET```
### URL params: ```id```

### **Code**: ```200 OK```
### Response example:
```json
{
  "sender_id": 1,
  "receiver_id": 2,
  "suggested_book_id": 1,
  "received_book_id": 2,
  "status": "string",
  "requested_date": "2025-04-28",
  "id": 1
}
```

## **URL**: ```/share_request/ ```
### Назначение: Создание запроса на обмен книгами
### **Method**: ```POST```
### Request body example:
```json
{
  "sender_id": 1,
  "receiver_id": 2,
  "suggested_book_id": 1,
  "received_book_id": 2,
  "status": "string",
  "requested_date": "2025-04-28"
}
```

### **Code**: ```201 Created```
### Response example:
```json
{
  "status": 201,
  "created": {
    "sender_id": 1,
    "receiver_id": 2,
    "suggested_book_id": 1,
    "received_book_id": 2,
    "status": "string",
    "requested_date": "2025-04-28",
    "id": 1
  }
}
```

## **URL**: ```/book_instance/{id} ```
### Назначение: Изменение запроса на обмен по id
### **Method**: ```PATCH```
### URL params: ```id```
### Request body example
```json
{
  "status": "upd"
}
```

### **Code**: ```200 OK```
### Response example:
```json
{
  "status": 202,
  "updated": {
    "sender_id": 1,
    "receiver_id": 2,
    "suggested_book_id": 1,
    "received_book_id": 2,
    "status": "upd",
    "requested_date": "2025-04-28",
    "id": 1
  }
}
```
