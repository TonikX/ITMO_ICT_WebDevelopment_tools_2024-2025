# Практики

## Создание базового приложения на FastAPI
**Установка FastApi**

`pip install fastapi`

Первый запуск
```
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def hello():
    return "Hello, [username]!"
```

![](test.png)
Первая документация
![](small_api.png)
Пошагово реализуем проект и методы
```
@app.get("/warriors_list")
def warriors_list() -> List[Warrior]:
    return temp_bd


@app.get("/warrior/{warrior_id}")
def get_warrior(warrior_id: int) -> List[Warrior]:
    return [w for w in temp_bd if w.get("id") == warrior_id]


@app.post("/warrior")
def create_warrior(warrior: Warrior) -> TypedDict('Response', {"status": int, "data": Warrior}):
    warrior_dict = warrior.model_dump()
    temp_bd.append(warrior_dict)
    return {"status": 200, "data": warrior}


@app.delete("/warrior/delete/{warrior_id}")
def delete_warrior(warrior_id: int):
    for i, w in enumerate(temp_bd):
        if w.get("id") == warrior_id:
            temp_bd.pop(i)
            break
    return {"status": 201, "message": "deleted"}


# === Professions ===
@app.get("/professions_list")
def professions_list() -> List[Profession]:
    return profession_temp_bd


@app.get("/profession/{profession_id}")
def get_profession(profession_id: int) -> List[Profession]:
    return [p for p in profession_temp_bd if p.get("id") == profession_id]


@app.post("/profession")
def create_profession(profession: Profession) -> TypedDict('Response', {"status": int, "data": Profession}):
    profession_dict = profession.model_dump()
    profession_temp_bd.append(profession_dict)
    return {"status": 200, "data": profession}


@app.delete("/profession/delete/{profession_id}")
def delete_profession(profession_id: int):
    for i, p in enumerate(profession_temp_bd):
        if p.get("id") == profession_id:
            profession_temp_bd.pop(i)
            break
    return {"status": 201, "message": "deleted"}
```
![](api.png)

Теперь для каждого запроса отображается описание в каком формате передаются и принимаются данные для каждого реализованного метода.
![](schemas.png)

## Настройка БД, SQLModel и миграции через Alembic

Установим библиотеку

`pip install sqlmodel`

Создадим подключение
```
from sqlmodel import SQLModel, create_engine, Session
# Строка подключения к PostgreSQL
DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/warriors_db"
engine = create_engine(DATABASE_URL, echo=True)
def init_db():
    SQLModel.metadata.create_all(engine)
def get_session():
    with Session(engine) as session:
        yield session
```

Необходимо добавить в main.py специальный метод on_startup с декоратором on_event вызывающий внутри инициализацию, чтобы описанные таблицы были созданы
```
@app.on_event("startup")
def on_startup():
    init_db()
```

## Миграции, ENV, GitIgnore и структура проекта

Для интеграции Alembic в разрабатываемый проект необходимо его установить через пакетный менеджер:
`pip install alembic`

Реализация механизма миграций происходит через вызов alembic init [name] в командной строке, где [name] — название папки, хранящей настройки миграций. Сгенерируем папку с миграциями и сопутствующие файлы настроек:

`alembic init migrations`

Получим структуру файлов:

![](migr.png)

Сгенерировалась папка migrations хранящая внутри себя папку с файлами миграций versions, файл окружения БД env.py и шаблон генерации миграций script.py.mako. В корне проекта добавился файл настроек alembic.ini