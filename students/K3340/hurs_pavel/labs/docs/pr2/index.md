# Документация по проекту Warriors API (PR2)

## Технический стек

- Python 3.x
- FastAPI
- SQLModel (ORM)
- PostgreSQL
- Docker

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

### RaceType (Тип расы)

```python
class RaceType(Enum):
    director = "director"
    worker = "worker"
    junior = "junior"
```

## API Endpoints

### Управление воинами

```http
POST /warrior - Создать нового воина
GET /warriors_list - Получить список всех воинов
GET /warrior/{warrior_id} - Получить информацию о воине
PATCH /warrior/{warrior_id} - Обновить информацию о воине
DELETE /warrior/delete/{warrior_id} - Удалить воина
POST /warrior/{warrior_id}/add_skill/{skill_id} - Добавить навык воину
```

### Управление профессиями

```http
GET /professions_list - Получить список всех профессий
GET /profession/{profession_id} - Получить информацию о профессии
POST /profession - Создать новую профессию
```

### Управление навыками

```http
GET /skills_list - Получить список всех навыков
GET /skill/{skill_id} - Получить информацию о навыке
POST /skill - Создать новый навык
PATCH /skill/{skill_id} - Обновить информацию о навыке
DELETE /skill/delete/{skill_id} - Удалить навык
```

## База данных

### Конфигурация

```python
db_url = 'postgresql://warrior:12345678@localhost:7432/warriors_db'
```

### Docker-конфигурация

```yaml
services:
  warriors-pr1-db:
    image: postgres:15
    environment:
      POSTGRES_USER: "warrior"
      POSTGRES_PASSWORD: "12345678"
      POSTGRES_DB: "warriors_db"
    ports:
      - "7432:5432"
```

## Особенности реализации

1. **Связи между таблицами:**

   - Many-to-Many между Warrior и Skill через SkillWarriorLink
   - One-to-Many между Profession и Warrior

2. **Валидация данных:**

   - Использование Pydantic моделей
   - Проверка существования связанных сущностей

3. **Обработка ошибок:**
   - HTTP исключения для несуществующих ресурсов
   - Проверка корректности данных

## Запуск проекта

1. Запуск базы данных:

```bash
docker-compose up -d
```

2. Установка зависимостей:

```bash
pip install fastapi sqlmodel psycopg2-binary uvicorn
```

3. Запуск API:

```bash
uvicorn main:app --reload
```

## API будет доступен:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
