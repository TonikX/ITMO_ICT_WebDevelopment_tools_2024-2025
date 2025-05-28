# Документация по проекту Warriors API (PR3)

## Технический стек

- Python 3.x
- FastAPI
- SQLModel (ORM)
- PostgreSQL
- Docker
- Alembic (миграции)

## Модели данных

### Warrior (Воин)

```python
class Warrior:
    id: int
    race: RaceType
    name: str
    level: int
    profession_id: Optional[int]
    profession: Optional[Profession]
    skills: Optional[List[Skill]]
```

### Profession (Профессия)

```python
class Profession:
    id: int
    title: str
    description: str
    warriors_prof: List[Warrior]
```

### Skill (Навык)

```python
class Skill:
    id: int
    name: str
    description: str
    warriors: Optional[List[Warrior]]
```

### SkillWarriorLink (Связь навыков с воинами)

```python
class SkillWarriorLink:
    skill_id: Optional[int]
    warrior_id: Optional[int]
    level: int | None
```

### RaceType (Тип расы)

```python
class RaceType(Enum):
    director = "director"
    worker = "worker"
    junior = "junior"
```

## База данных

### Конфигурация

База данных управляется через переменные окружения:

```python
DB_ADMIN = 'postgresql://warrior:12345678@localhost:8432/warriors_db'
```

### Docker-конфигурация

```yaml
services:
  warriors-pr3-db:
    image: postgres:15
    environment:
      POSTGRES_USER: "warrior"
      POSTGRES_PASSWORD: "12345678"
      POSTGRES_DB: "warriors_db"
    ports:
      - "8432:5432"
```

## Миграции

Проект использует Alembic для управления миграциями базы данных:

- Файлы миграций находятся в папке `migrations/`
- Конфигурация в `alembic.ini`
- Скрипты миграций автоматически генерируются

## Основные улучшения от PR2

1. Добавлен уровень навыка для связи Warrior-Skill
2. Улучшена система миграций
3. Оптимизирована работа с Docker
4. Добавлены переменные окружения
5. Улучшена производительность базы данных

## Запуск проекта

1. Запуск базы данных:

```bash
docker-compose up -d
```

2. Установка зависимостей:

```bash
pip install fastapi sqlmodel psycopg2-binary alembic python-dotenv
```

3. Применение миграций:

```bash
alembic upgrade head
```

4. Запуск API:

```bash
uvicorn main:app --reload
```

## Доступ к API

- API доступно по адресу: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Особенности реализации

1. Использование SQLModel для типизированной работы с базой данных
2. Поддержка миграций через Alembic
3. Контейнеризация базы данных
4. Улучшенная система связей между моделями
5. Оптимизированная конфигурация Docker

## Структура проекта

```
PR3/
├── migrations/         # Файлы миграций
├── models.py          # Модели данных
├── connection.py      # Подключение к БД
├── docker-compose.yaml # Docker конфигурация
└── alembic.ini        # Конфигурация миграций
```
