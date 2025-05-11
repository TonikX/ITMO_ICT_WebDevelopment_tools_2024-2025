## **URL**: ```/login/ ```

### Назначение: Авторизация в системе
### **Method**: ```POST```
### Request Body example:
```json
{
  "email": "test@mail.ru",
  "password": "piupiupiu"
}
```

### **Code**: ```200 OK```

### Response example:
```json
{
  "status": 200,
  "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDU4MzQ0MzksImlhdCI6MTc0NTgzMjYzOSwic3ViIjoiMyJ9.awMdSoxd6warsWRbqVClpZprBJnQ4tTRQ1KSsdObcp4"
}
```

## **URL**: ```/register/ ```
### Назначение: Регистрация в системе
### **Method**: ```POST```
### Request Body example:
```json
{
  "name": "NoName",
  "password": "12345",
  "email": "test@mail.ru",
  "description": "string",
  "register_date": "2025-04-28",
  "birth_date": "2025-04-28"
}
```

### **Code**: ```201 Created```
### Response example:
```json
{
  "status": 201,
  "created": {
    "name": "NoName",
    "password": "hash",
    "email": "test@mail.ru",
    "description": "string",
    "register_date": "2025-04-28",
    "birth_date": "2025-04-28",
    "id": 1
  }
}
```