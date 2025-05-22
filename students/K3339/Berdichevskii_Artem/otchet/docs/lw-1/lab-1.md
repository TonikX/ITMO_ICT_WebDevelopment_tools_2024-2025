# Лабораторная работа №1: Веб-приложение с Docker и Alembic

## 📘 Описание проекта
Проект представляет собой контейнеризированное Python-приложение, построенное с использованием **Docker**, **FastAPI** и **Alembic** для управления миграциями базы данных. Вся логика находится в директории `app/`, контейнеризация обеспечивается через `Dockerfile` и `docker-compose`.

---

## 📁 Структура проекта

```
lr1/
├── .env                  # Переменные окружения
├── Dockerfile            # Сборка контейнера
├── docker-compose.yaml  # Компоновка сервисов
├── requirements.txt      # Python-зависимости
├── alembic.ini           # Настройка Alembic
├── app/
│   ├── main.py           # Основной модуль FastAPI
│   ├── database.py       # Подключение к БД
│   ├── start.sh          # Скрипт запуска
│   └── repositories/     # Логика работы с данными
```

---

## 🚀 Установка и запуск

### 🔧 Предварительные требования
- Docker
- Docker Compose

### ▶️ Запуск

```bash
# Клонирование проекта
$ git clone <repo-url>
$ cd lr1

# Копирование переменных окружения
$ cp .env.example .env

# Запуск приложения в контейнере
$ docker-compose up --build
```

После запуска приложение будет доступно по адресу: [http://localhost:8000](http://localhost:8000)

---

## 🧩 Основные модули и примеры кода

### 📄 `main.py`
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
```

Простой HTTP GET обработчик, возвращающий JSON-ответ при обращении к корню API.

### 🗃 `database.py`
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
```

Модуль настройки подключения к базе данных.

---

## 🧱 Репозитории и модели

### 👤 User
Файл: `repositories/user.py`
- Методы: `get_by_email`, `get_by_username`, `create`, `update_password`
- Используемая модель: `User`

```python
async def get_by_email(self, db, email):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()
```

Создание пользователя с хешированием пароля:
```python
hashed_password = get_password_hash(obj_in.password)
```

### 📋 Task
Файл: `repositories/task.py`
- Метод: `get_by_event_id`
- Модель: `Task`

```python
statement = select(Task).filter(Task.event_id == event_id)
```

Возвращает список заданий, привязанных к событию.

### 👥 Team
Файл: `repositories/team.py`
- Методы: `get_event_teams`, `get_user_teams`, `get_by_user_event`
- Модель: `Team`

```python
select(Team).join(Registration).where(Registration.user_id == user.id)
```

Получение всех команд пользователя или команд по событию.

### 🎉 Event
Файл: `repositories/event.py`
- Метод: `filter_events_by_dates`
- Модель: `Event`

```python
if from_date:
    query = query.filter(self.model.dt_event_start >= from_date)
```

Фильтрация событий по датам начала/окончания/регистрации.

---

## 🛠 Работа с Alembic

### Инициализация Alembic
```bash
$ alembic init alembic
```

### Создание миграции
```bash
$ alembic revision --autogenerate -m "Initial migration"
```

### Применение миграций
```bash
$ alembic upgrade head
```

---

## 📎 Пример запроса

- **URL**: `GET /`
- **Ответ**: `{ "message": "Hello, World!" }`

Можно протестировать через браузер или cURL:
```bash
$ curl http://localhost:8000/
```

Ссылка на репозиторий: https://github.com/berdichevskiia/ITMO_ICT_WebDevelopment_tools_2023-2024/tree/lr1

![Задача 1](/Users/artemberdichevskii/PycharmProjects/ITMO_ICT_WebDevelopment_tools_2023-2024/students/K3339/Berdichevskii_Artem/otchet/docs/pic/1_task.png)

![Решение задачи 1](/Users/artemberdichevskii/PycharmProjects/ITMO_ICT_WebDevelopment_tools_2023-2024/students/K3339/Berdichevskii_Artem/otchet/docs/pic/1_answer.png)


![Задача 2](/Users/artemberdichevskii/PycharmProjects/ITMO_ICT_WebDevelopment_tools_2023-2024/students/K3339/Berdichevskii_Artem/otchet/docs/pic/2_task.png)

![Решение задачи 2](/Users/artemberdichevskii/PycharmProjects/ITMO_ICT_WebDevelopment_tools_2023-2024/students/K3339/Berdichevskii_Artem/otchet/docs/pic/2_answer.png)