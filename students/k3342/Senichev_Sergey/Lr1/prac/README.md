# API управления задачами на FastAPI

Проект представляет собой RESTful API для управления задачами и спринтами с использованием:
- **FastAPI** для веб-сервера
- **SQLAlchemy** для ORM
- **PostgreSQL** в качестве базы данных
- **Alembic** для миграций базы данных
- **Pydantic** для валидации данных

## Структура проекта

```
prac2/
├── config.py                 # Настройки конфигурации
├── __init__.py              
├── db/                       # Модуль базы данных
│   ├── database.py           # Подключение к БД
│   ├── __init__.py
│   └── models.py             # Модели SQLAlchemy
└── rest/                     # API эндпоинты
    ├── app.py                # Основное приложение FastAPI
    ├── __init__.py
    ├── sprint/               # API для спринтов
    ├── task/                 # API для задач
    └── task_link/            # API для связей между задачами
```

## Установка и запуск

1. Установите зависимости:
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv pydantic pydantic-settings alembic
```

2. Создайте файл `.env` в директории `/fastapi` с настройками базы данных:
```
DATABASE__HOST=localhost
DATABASE__PORT=5432
DATABASE__USER=postgres
DATABASE__PASSWORD=ваш_пароль
DATABASE__NAME=task_management_db
```

3. Создайте базу данных в PostgreSQL:
```sql
CREATE DATABASE task_management_db;
```

4. Примените миграции:
```bash
python apply_migrations.py
```

5. Запустите сервер:
```bash
uvicorn students.k3342.practical_works.Senichev_Sergey.fastapi.prac2.rest.app:app --reload
```

6. Откройте в браузере:
- API документация (Swagger UI): http://localhost:8000/docs
- Альтернативная документация (ReDoc): http://localhost:8000/redoc

## API эндпоинты

### Задачи
- `GET /tasks` - получить все задачи (с вложенными связями)
- `GET /tasks/{task_id}` - получить задачу по ID
- `POST /tasks` - создать новую задачу
- `PATCH /tasks/{task_id}` - обновить задачу
- `DELETE /tasks/{task_id}` - удалить задачу

### Спринты
- `GET /sprints` - получить все спринты
- `GET /sprints/{sprint_id}` - получить спринт по ID
- `POST /sprints` - создать новый спринт
- `PATCH /sprints/{sprint_id}` - обновить спринт
- `DELETE /sprints/{sprint_id}` - удалить спринт

### Связи между задачами
- `GET /task_links` - получить все связи
- `GET /task_links/{child_task_id}/{parent_task_id}` - получить связь
- `POST /task_links` - создать новую связь
- `PATCH /task_links/{child_task_id}/{parent_task_id}` - обновить связь
- `DELETE /task_links/{child_task_id}/{parent_task_id}` - удалить связь

## Миграции

Для управления миграциями используется Alembic:

- Создание новой миграции:
```bash
python create_migration.py
```

- Применение миграций:
```bash
python apply_migrations.py
``` 