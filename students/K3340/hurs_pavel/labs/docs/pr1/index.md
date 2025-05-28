# Документация по проекту Time Manager API (PR1)

## Основные возможности

- Управление воинами (warriors)
- Управление профессиями (professions)
- Базовая система навыков (skills)

## Технический стек

- Python 3.x
- FastAPI
- Pydantic для валидации данных
- Временное хранение данных в памяти

## Модели данных

### Warrior (Воин)

```python
class Warrior:
    id: int
    race: RaceType
    name: str
    level: int
    profession: Profession
    skills: Optional[List[Skill]]
```

### Profession (Профессия)

```python
class Profession:
    id: int
    title: str
    description: str
```

### Skill (Навык)

```python
class Skill:
    id: int
    name: str
    description: str
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
GET /warriors_list - Получить список всех воинов
GET /warrior/{warrior_id} - Получить информацию о конкретном воине
POST /warrior - Создать нового воина
PUT /warrior{warrior_id} - Обновить информацию о воине
DELETE /warrior/delete{warrior_id} - Удалить воина
```

### Управление профессиями

```http
GET /professions - Получить список всех профессий
GET /profession/{profession_id} - Получить информацию о конкретной профессии
POST /profession - Создать новую профессию
PUT /profession/{profession_id} - Обновить информацию о профессии
DELETE /profession/{profession_id} - Удалить профессию
```

## Формат данных

### Пример создания воина

```json
{
  "id": 1,
  "race": "director",
  "name": "Иванов Иван",
  "level": 15,
  "profession": {
    "id": 1,
    "title": "Главный директор",
    "description": "Опытный руководитель, эксперт по стратегическому планированию"
  },
  "skills": [
    {
      "id": 1,
      "name": "Планирование и управление ресурсами",
      "description": "Знание передовых методик управления"
    }
  ]
}
```

## Особенности реализации

1. Данные хранятся в памяти (временная база данных `temp_bd`)
2. Используется валидация данных с помощью Pydantic моделей
3. Реализована базовая обработка ошибок
4. Поддержка CRUD операций для основных сущностей

## Запуск проекта

1. Установите зависимости:

```bash
pip install fastapi uvicorn pydantic
```

2. Запустите сервер:

```bash
uvicorn main:app --reload
```

3. API будет доступно по адресу: `http://localhost:8000`
4. Документация Swagger UI: `http://localhost:8000/docs`
