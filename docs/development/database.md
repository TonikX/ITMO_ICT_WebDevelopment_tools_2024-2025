# База данных

В этом разделе описана структура базы данных API Поиска Веб-Команд.

## Схема базы данных

API Поиска Веб-Команд использует PostgreSQL в качестве системы управления базами данных. Схема базы данных состоит из следующих основных таблиц:

### Пользователи (User)

Таблица `user` хранит информацию о пользователях системы.

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Первичный ключ |
| username | String | Уникальное имя пользователя |
| full_name | String | Полное имя пользователя |
| email | String | Электронная почта пользователя (уникальная) |
| hashed_password | String | Хешированный пароль пользователя |
| bio | String | Биография пользователя (опционально) |
| years_of_experience | Float | Опыт работы в годах |
| is_active | Boolean | Активен ли пользователь |
| created_at | DateTime | Дата и время создания пользователя |

### Навыки (Skill)

Таблица `skill` хранит информацию о навыках, которыми могут обладать пользователи.

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Первичный ключ |
| name | String | Название навыка |
| category | String | Категория навыка |
| description | String | Описание навыка (опционально) |
| created_at | DateTime | Дата и время создания навыка |

### Связь пользователей и навыков (UserSkillLink)

Таблица `user_skill_link` связывает пользователей с их навыками и указывает уровень владения навыком.

| Поле | Тип | Описание |
|------|-----|----------|
| user_id | Integer | Внешний ключ на таблицу `user` |
| skill_id | Integer | Внешний ключ на таблицу `skill` |
| level | Enum | Уровень владения навыком (beginner, intermediate, advanced, expert) |

### Команды (Team)

Таблица `team` хранит информацию о командах.

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Первичный ключ |
| name | String | Название команды |
| description | String | Описание команды (опционально) |
| created_at | DateTime | Дата и время создания команды |

### Связь пользователей и команд (TeamMemberLink)

Таблица `team_member_link` связывает пользователей с командами и указывает роль пользователя в команде.

| Поле | Тип | Описание |
|------|-----|----------|
| team_id | Integer | Внешний ключ на таблицу `team` |
| user_id | Integer | Внешний ключ на таблицу `user` |
| role | Enum | Роль пользователя в команде (leader, member, mentor) |

### Проекты (Project)

Таблица `project` хранит информацию о проектах.

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Первичный ключ |
| title | String | Название проекта |
| description | String | Описание проекта |
| start_date | DateTime | Дата начала проекта |
| end_date | DateTime | Дата окончания проекта (опционально) |
| status | String | Статус проекта |

### Связь проектов и команд (ProjectTeamLink)

Таблица `project_team_link` связывает проекты с командами, работающими над ними.

| Поле | Тип | Описание |
|------|-----|----------|
| project_id | Integer | Внешний ключ на таблицу `project` |
| team_id | Integer | Внешний ключ на таблицу `team` |

### Связь проектов и навыков (ProjectSkillLink)

Таблица `project_skill_link` связывает проекты с рекомендуемыми навыками для участия в них.

| Поле | Тип | Описание |
|------|-----|----------|
| project_id | Integer | Внешний ключ на таблицу `project` |
| skill_id | Integer | Внешний ключ на таблицу `skill` |

### Задачи (Task)

Таблица `task` хранит информацию о задачах в проектах.

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Первичный ключ |
| title | String | Название задачи |
| description | String | Описание задачи |
| status | String | Статус задачи (not_started, in_progress, review, completed) |
| priority | String | Приоритет задачи (low, medium, high, critical) |
| due_date | DateTime | Срок выполнения задачи |
| project_id | Integer | Внешний ключ на таблицу `project` |
| assigned_user_id | Integer | Внешний ключ на таблицу `user` (пользователь, которому назначена задача) |
| created_at | DateTime | Дата и время создания задачи |

## Диаграмма базы данных

Ниже представлена диаграмма связей между таблицами базы данных:

```
+----------------+       +-------------------+       +----------------+
|     User       |       | UserSkillLink     |       |     Skill      |
+----------------+       +-------------------+       +----------------+
| id             |<----->| user_id           |<----->| id             |
| username       |       | skill_id          |       | name           |
| full_name      |       | level             |       | category       |
| email          |       +-------------------+       | description    |
| hashed_password|                                   | created_at     |
| bio            |                                   +----------------+
| years_of_exp   |                                           ^
| is_active      |                                           |
| created_at     |                                   +-------------------+
+----------------+                                   | ProjectSkillLink  |
        ^                                            +-------------------+
        |                                            | project_id        |
        |                                            | skill_id          |
+-------------------+                                +-------------------+
| TeamMemberLink    |                                        ^
+-------------------+                                        |
| team_id           |                                        |
| user_id           |                                +----------------+
| role              |                                |    Project     |
+-------------------+                                +----------------+
        ^                                            | id             |
        |                                            | title          |
+----------------+       +-------------------+       | description    |
|     Team       |       | ProjectTeamLink   |       | start_date     |
+----------------+       +-------------------+       | end_date       |
| id             |<----->| team_id           |<----->| status         |
| name           |       | project_id        |       | created_at     |
| description    |       +-------------------+       +----------------+
| created_at     |                                           ^
+----------------+                                           |
                                                             |
                                                    +----------------+
                                                    |     Task       |
                                                    +----------------+
                                                    | id             |
                                                    | title          |
                                                    | description    |
                                                    | status         |
                                                    | priority       |
                                                    | due_date       |
                                                    | project_id     |
                                                    | assigned_user_id|
                                                    | created_at     |
                                                    +----------------+
```

## Миграции базы данных

Для управления схемой базы данных используется Alembic - инструмент миграции для SQLAlchemy. Миграции позволяют отслеживать изменения в схеме базы данных и применять их последовательно.

### Основные команды Alembic

1. Создание новой миграции:

```bash
alembic revision --autogenerate -m "Описание изменений"
```

2. Применение всех ожидающих миграций:

```bash
alembic upgrade head
```

3. Откат последней миграции:

```bash
alembic downgrade -1
```

4. Просмотр текущей версии базы данных:

```bash
alembic current
```

### Структура миграций

Миграции хранятся в директории `migrations/versions/`. Каждый файл миграции содержит две функции:

- `upgrade()` - применяет изменения к базе данных
- `downgrade()` - отменяет изменения, внесенные функцией `upgrade()`

## Подключение к базе данных

Подключение к базе данных осуществляется через SQLModel (надстройка над SQLAlchemy). Параметры подключения хранятся в файле `.env`:

```
DB_USERNAME=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_NAME=web_team_finder
```

Код подключения к базе данных находится в файле `connection.py`:

```python
import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine

load_dotenv()
username = os.getenv("DB_USERNAME", "postgres")
password = os.getenv("DB_PASSWORD", "")
host = os.getenv("DB_HOST", "localhost")
database = os.getenv("DB_NAME", "web_team_finder")

db_url = f'postgresql://{username}:{password}@{host}/{database}'
engine = create_engine(db_url, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```
