# Документация к сервису управления финансами

## Описание проекта
Данный сервис предоставляет API для управления личными финансами. Он позволяет пользователям:
- Регистрацию и авторизацию (с поддержкой смены пароля)
- Ведение бюджета, учет доходов и расходов
- Управление категориями расходов
- Анализ трат по категориям

Сервис разработан на **FastAPI** с использованием **Pydantic** для валидации данных и **PostgreSQL** в качестве базы данных.

---

## Запуск

### 1. Применение миграций для базы данных
```bash
alembic upgrade head
```

### 2. Запуск сервера
```bash
uvicorn main:app --reload
```

После этого API будет доступно по адресу:  
[http://127.0.0.1:8000/docs](http://127.0.0.1:4200/docs)   

---

## Конфигурационные файлы

### `.env`
```ini
DATABASE_URL=postgresql://***:***@***:***/finance_db
SECRET_KEY=supersecretkey
```

### `alembic.ini`
```ini
[alembic]
script_location = alembic

sqlalchemy.url = postgresql://postgres:12345678@localhost:5432/finance_db

[loggers]
keys = root,sqlalchemy,alembic

[logger_alembic]
level = INFO
qualname = alembic
```

---

## Структура проекта
```plaintext
finance-manager/
│── alembic/              # Миграции базы данных
│── routers/              # Маршруты API
│   ├── auth.py           # Авторизация и аутентификация
│   ├── transactions.py   # Операции с транзакциями
│   ├── categories.py     # Категории трат
│   ├── budgets.py        # Бюджетирование
│   ├── analytics.py      # Аналитика расходов
│── schemas/              # Pydantic-схемы
│── models/               # SQLAlchemy-модели
│── database.py           # Подключение к БД
│── main.py               # Запуск FastAPI-приложения
│── requirements.txt      # Зависимости проекта
│── .env                  # Переменные окружения
```

---

## Основные API-эндпоинты

### Авторизация
#### Регистрация пользователя
**POST** `/auth/register`
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

#### Вход (получение токена)
**POST** `/auth/login`
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```
**Ответ:**
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

---

### Транзакции
#### Создание транзакции
**POST** `/transactions`
```json
{
  "amount": 1500,
  "date": "2025-03-25T12:00:00",
  "description": "Покупка ноутбука",
  "type": "expense",
  "category_id": 2,
  "weight": 1.5
}
```

#### Получение всех транзакций пользователя
**GET** `/transactions`

---

### Аналитика
#### Получение отчетов по категориям расходов
**GET** `/analytics/expenses`
**Ответ:**
```json
[
  {
    "category": "Продукты",
    "total_spent": 5000
  },
  {
    "category": "Развлечения",
    "total_spent": 2000
  }
]
```

---

## Pydantic-схемы

### `schemas/budget.py`
```python
from pydantic import BaseModel

class BudgetBase(BaseModel):
    limit: float
    category_id: int

class BudgetCreate(BudgetBase):
    pass

class BudgetResponse(BudgetBase):
    id: int
    user_id: int
    category_name: str

    class Config:
        from_attributes = True
```

### `schemas/user.py`
```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True
```

---

### Миграции (Alembic)
#### Создание миграции
```bash
alembic revision --autogenerate -m "Добавлены таблицы"
```
#### Применение миграций
```bash
alembic upgrade head
```

---


