## **URL**: ```/book_instance/{id} ```
### Назначение: Получение экземпляра по id
### **Method**: ```GET```
### URL params: ```id```

### **Code**: ```200 OK```
### Response example:
```json
{
  "owner_id": 0,
  "info_id": 0,
  "print_date": "2025-04-28",
  "own_since": "2025-04-28",
  "id": 0,
  "owner": {
    "name": "string",
    "password": "string",
    "email": "string",
    "description": "string",
    "register_date": "2025-04-28",
    "birth_date": "2025-04-28"
  }
}
```

## **URL**: ```/book_instance/ ```
### Назначение: Создание экземпляра книги
### **Method**: ```POST```
### Request body example:
```json
{
  "owner_id": 1,
  "info_id": 2,
  "print_date": "2025-04-28",
  "own_since": "2025-04-28"
}
```

### **Code**: ```201 Created```
### Response example:
```json
{
  "status": 201,
  "created": {
    "owner_id": 1,
    "info_id": 2,
    "print_date": "2025-04-28",
    "own_since": "2025-04-28",
    "id": 3
  }
}
```

## **URL**: ```/book_info_list/ ```
### Назначение: Получение данных о всех книгах
### **Method**: ```GET```

### **Code**: ```200 OK```
### Response example:
```json
[
  {
    "author": "Sholohov Michail",
    "release_date": "1928-01-01",
    "genre": "roman",
    "title": "Tihiy Don",
    "publisher": "October",
    "id": 2
  },
  {
    "author": "Nosov Nikolay",
    "release_date": "1958-01-01",
    "genre": "utopia",
    "title": "Neznaika",
    "publisher": "Юность",
    "id": 3
  },
  {
    "author": "Нимцович А.",
    "release_date": "1925-01-01",
    "genre": "Нон-фикшн",
    "title": "Моя Система",
    "publisher": "-",
    "id": 4
  }
]
```

## **URL**: ```/book_info/ ```
### Назначение: Создание книги
### **Method**: ```POST```
### Request body example:
```json
{
  "title": "string",
  "author": "string",
  "release_date": "2025-04-28",
  "publisher": "string",
  "genre": "string"
}
```

### **Code**: ```201 Created```
### Response example:
```json
{
  "status": 201,
  "created": {
    "title": "string",
    "author": "string",
    "release_date": "2025-04-28",
    "publisher": "string",
    "genre": "string",
    "id": 1
  }
}
```