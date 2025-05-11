## **URL**: ```/profile_list/ ```
### Назначение: Получение данных о пользователях
### **Method**: ```GET```

### **Code**: ```200 OK```
### Response example:
```json
[
  {
    "name": "string",
    "password": "string",
    "email": "string",
    "description": "string",
    "register_date": "2025-04-14",
    "birth_date": "2025-04-14",
    "id": 2,
    "books": [
      {
        "own_since": "2001-02-03",
        "owner_id": 2,
        "print_date": "1957-06-21",
        "info_id": 4
      }
    ],
    "sent_requests": [],
    "received_requests": [
      {
        "receiver_id": 2,
        "received_book_id": 5,
        "requested_date": "2025-04-28",
        "suggested_book_id": 4,
        "sender_id": 3,
        "status": "created"
      }
    ]
  },
  {
    "name": "dafa",
    "password": "WLNiMjf49TxVdgvGrTw11V5mmNb01/+fNpe+BpZTOxs=",
    "email": "dafahaha@mail.ru",
    "description": "...",
    "register_date": "2025-04-28",
    "birth_date": "2004-01-14",
    "id": 3,
    "books": [
      {
        "own_since": "2009-09-20",
        "owner_id": 3,
        "print_date": "2009-03-21",
        "info_id": 3
      },
      {
        "own_since": "2020-09-03",
        "owner_id": 3,
        "print_date": "2005-01-21",
        "info_id": 2
      }
    ],
    "sent_requests": [
      {
        "receiver_id": 2,
        "received_book_id": 5,
        "requested_date": "2025-04-28",
        "suggested_book_id": 4,
        "sender_id": 3,
        "status": "created"
      }
    ],
    "received_requests": []
  }
]
```

## **URL**: ```/profile/{id} ```
### Назначение: Получение профиля по id
### **Method**: ```GET```
### URL params: ```id```

### **Code**: ```200 OK```
### Response example:
```json
{
  "name": "string",
  "password": "string",
  "email": "string",
  "description": "string",
  "register_date": "2025-04-28",
  "birth_date": "2025-04-28",
  "id": 0,
  "books": [],
  "sent_requests": [],
  "received_requests": []
}
```


## **URL**: ```/profile/{id} ```
### Назначение: Удаление профиля по id
### **Method**: ```DELETE```
### URL params: ```id```

### **Code**: ```200 OK```
### Response example:
```json
{
  "status": 204,
  "msg": "string"
}
```
