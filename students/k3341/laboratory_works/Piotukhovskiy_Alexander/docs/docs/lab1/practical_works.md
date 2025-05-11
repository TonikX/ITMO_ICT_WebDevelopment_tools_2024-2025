# Практическая работа 1
Создание базового приложения на FastAPI

Для начала была выполнена установка и настройка окружения  
```shell
python -m venv venv
source venv/Scripts/activate
pip install fastapi[all]
```

Для выполнения базовых CRUD операций в файле `main.py` была создана временная база данных:  
```python
temp_bd = [
{
    "id": 1,
    "race": "director",
    "name": "Мартынов Дмитрий",
    "level": 12,
    "profession": {
        "id": 1,
        "title": "Влиятельный человек",
        "description": "Эксперт по всем вопросам"
    },
    "skills":
        [{
            "id": 1,
            "name": "Купле-продажа компрессоров",
            "description": ""

        },
        {
            "id": 2,
            "name": "Оценка имущества",
            "description": ""

        }]
},
{
    "id": 2,
    "race": "worker",
    "name": "Андрей Косякин",
    "level": 12,
    "profession": {
        "id": 1,
        "title": "Дельфист-гребец",
        "description": "Уважаемый сотрудник"
    },
    "skills": []
},
]

temp_professions = [
    {"id": 1, "title": "Влиятельный человек", "description": "Эксперт по всем вопросам"},
    {"id": 2, "title": "Дельфист-гребец", "description": "Уважаемый сотрудник"}
]
```

Для сериализации и десериализации данных были созданы pydantic модели. 
Они находятся в файле `models.py` и описывают структуру данных, хранящуюся в БД:  
```python
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel

class Profession(BaseModel):
    id: int
    title: str
    description: str

class Skill(BaseModel):
    id: int
    name: str
    description: str


class RaceType(Enum):
    director = "director"
    worker = "worker"
    junior = "junior"

class Warrior(BaseModel):
    id: int
    race: RaceType
    name: str
    level: int
    profession: Profession
    skills: Optional[List[Skill]] = []
```

Были созданы api эндпоинты для проведения базовых CRUD операций над войнами:
```python
@app.get("/warriors_list")
def warriors_list() -> tp.List[Warrior]:
    return temp_bd


@app.get("/warrior/{warrior_id}")
def warriors_list(warrior_id: int) -> List[Warrior]:
    return [warrior for warrior in temp_bd if warrior.get("id") == warrior_id]


@app.post("/warrior")
def warriors_list(warrior: dict) -> TypedDict('Response', {"status": int, "data": Warrior}):
    temp_bd.append(warrior)
    return {"status": 200, "data": warrior}


@app.put("/warrior{warrior_id}")
def warrior_update(warrior_id: int, warrior: dict) -> List[Warrior]:
    for i, war in enumerate(temp_bd):
        if war.get("id") == warrior_id:
            temp_bd[i] = warrior
    return temp_bd


@app.delete("/warrior/delete{warrior_id}")
def warrior_delete(warrior_id: int):
    for i, warrior in enumerate(temp_bd):
        if warrior.get("id") == warrior_id:
            temp_bd.pop(i)
            break
    return {"status": 200, "message": "deleted"}
```

По аналогии были созданы CRUD операции для профессий:
```python
@app.get("/professions")
def get_professions() -> tp.List[Profession]:
    return temp_professions

@app.get("/profession/{profession_id}")
def get_profession(profession_id: int) -> Profession:
    for profession in temp_professions:
        if profession.get("id") == profession_id:
            return profession
    raise HTTPException(status_code=404, detail="Профессия не найдена")

@app.post("/profession")
def create_profession(profession: Profession) -> TypedDict('Response', {"status": int, "data": Profession}):
    temp_professions.append(profession.dict())
    return {"status": 200, "data": profession}

@app.put("/profession/{profession_id}")
def update_profession(profession_id: int, profession: Profession) -> tp.List[Profession]:
    for i, prof in enumerate(temp_professions):
        if prof.get("id") == profession_id:
            temp_professions[i] = profession.dict()
            return temp_professions
    raise HTTPException(status_code=404, detail="Профессия не найдена")

@app.delete("/profession/{profession_id}")
def delete_profession(profession_id: int):
    for i, prof in enumerate(temp_professions):
        if prof.get("id") == profession_id:
            temp_professions.pop(i)
            return {"status": 200, "message": "deleted"}
    raise HTTPException(status_code=404, detail="Профессия не найдена")
```

---

# Практическая работа 2
Настройка базы данных, SQLModel

Для добавления ORM в код необходимо установить соответствующие зависимости. Работать будем с базой данный **PostgreSQL** и библиотекой **sqlmodel**, которая "под капотом" использует SQLAlchemy. Нам потребуется установить драйвер для взаимодействия с PostgreSQL и sqlmodel.
```shell
pip install sqlmodel psycopg2-binary
```

В файле `connection.py` представлены данные для подключения к базе данных PostgreSQL:
```python
from sqlmodel import SQLModel, Session, create_engine

db_url = "postgresql://postgres:youshallnotpass@localhost:5432/warriors_db"
engine = create_engine(db_url, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```

Функция `get_session()` будет предоставлять сессию для каждого запроса. Все таблицы создаются при запуске приложения посредством функции `init_db()`:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
```

Все модели в файле `models.py` были переписаны с pydantic на SQLModel:
```python
class RaceType(Enum):
    director = "director"
    worker = "worker"
    junior = "junior"


class SkillWarriorLink(SQLModel, table=True):
    skill_id: Optional[int] = Field(
        default=None, foreign_key="skill.id", primary_key=True
    )
    warrior_id: Optional[int] = Field(
        default=None, foreign_key="warrior.id", primary_key=True
    )


class SkillDefault(SQLModel):
    name: str
    description: Optional[str] = ""


class Skill(SkillDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    warriors: Optional[List["Warrior"]] = Relationship(
        back_populates="skills", link_model=SkillWarriorLink
    )


class ProfessionDefault(SQLModel):
    title: str
    description: str


class Profession(ProfessionDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    warriors_prof: List["Warrior"] = Relationship(back_populates="profession")


class WarriorDefault(SQLModel):
    race: RaceType
    name: str
    level: int
    profession_id: Optional[int] = Field(default=None, foreign_key="profession.id")


class Warrior(WarriorDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    profession: Optional[Profession] = Relationship(
        back_populates="warriors_prof",
        sa_relationship_kwargs={"lazy": "joined"},
    )

    skills: Optional[List[Skill]] = Relationship(
        back_populates="warriors",
        link_model=SkillWarriorLink,
        sa_relationship_kwargs={"uselist": True, "lazy": "selectin"},
    )


class WarriorProfessions(WarriorDefault):
    profession: Optional[Profession] = None


class WarriorResponse(WarriorProfessions):
    id: int
    skills: List[Skill]
```

Теперь во всех эндпоинтах мы получаем / создаем / обновляем / удаляем объекты при помощи объекта сессии и храним все информацию в базе данных:
```python
@app.get("/warriors_list")
def warriors_list(session=Depends(get_session)) -> List[Warrior]:
    return session.exec(select(Warrior)).all()


@app.get("/warrior/{warrior_id}", response_model=WarriorResponse)
def warriors_get(warrior_id: int, session=Depends(get_session)) -> Warrior:
    warrior = session.get(Warrior, warrior_id)
    return warrior


@app.post("/warrior")
def warriors_create(warrior: WarriorDefault, session=Depends(get_session)):
    warrior = Warrior.model_validate(warrior)
    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return {"status": 200, "data": warrior}


@app.patch("/warrior/{warrior_id}")
def warrior_update(warrior_id: int, warrior: WarriorDefault, session=Depends(get_session)) -> WarriorDefault:
    db_warrior = session.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")

    warrior_data = warrior.model_dump(exclude_unset=True)
    for key, value in warrior_data.items():
        setattr(db_warrior, key, value)

    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior


@app.delete("/warrior/{warrior_id}")
def warrior_delete(warrior_id: int, session=Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(warrior)
    session.commit()
    return {"status": 204}


@app.get("/professions")
def professions_list(session=Depends(get_session)) -> List[Profession]:
    return session.exec(select(Profession)).all()


@app.get("/profession/{profession_id}")
def profession_get(profession_id: int, session=Depends(get_session)) -> Profession:
    return session.get(Profession, profession_id)


@app.post("/profession")
def profession_create(prof: ProfessionDefault, session=Depends(get_session)):
    prof = Profession.model_validate(prof)
    session.add(prof)
    session.commit()
    session.refresh(prof)
    return {"status": 201, "data": prof}
```

В рамках практической работы также были добавлены API эндпоинты для проведения CRUD операций над умениями воинов:
```python
@app.get("/skills")
def skills_list(session=Depends(get_session)) -> List[Skill]:
    return session.exec(select(Skill)).all()


@app.post("/skills")
def skill_create(skill: SkillDefault, session=Depends(get_session)):
    skill = Skill.model_validate(skill)
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return {"status": 201, "data": skill}


@app.patch("/skills/{skill_id}")
def skill_update(
    skill_id: int,
    skill: SkillDefault,
    session=Depends(get_session),
) -> SkillDefault:
    db_skill = session.get(Skill, skill_id)
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    skill_data = skill.model_dump(exclude_unset=True)
    for key, value in skill_data.items():
        setattr(db_skill, key, value)

    session.add(db_skill)
    session.commit()
    session.refresh(db_skill)
    return db_skill


@app.delete("/skills/{skill_id}")
def skill_delete(skill_id: int, session=Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    session.delete(skill)
    session.commit()
    return {"status": 204}
```

И эндпоинт для создания ассоциаций между воинами и умениями:
```python
@app.post("/skill_warriors")
def warrior_slill_add(skill_warrior: SkillWarriorLink, session=Depends(get_session)):
    skill = session.get(Skill, skill_warrior.skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    warrior = session.get(Warrior, skill_warrior.warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")

    if skill not in warrior.skills:
        session.add(skill_warrior)
        session.commit()

    return {"status": 204}
```

---

# Практическая работа 3
Создание миграции, env, gitignore

В качестве инструмента миграций используем Alembic:
```shell
pip install alembic
alembic init alembic
```
Где второй раз указывается alembic - название папки, в которой будут сохранены миграции.

Так как мы используем sqlmodel, библиотеку необходимо импортировать в шаблоне генерации миграций:
```python
...
from typing import Sequence, Union

import sqlmodel # Добавили этот импорт
from alembic import op
import sqlalchemy as sa
...
```

Теперь необходимо создать и использовать переменные окружения. Создадим `.env` файл в корне проекта, в него запишем данные для подключения к базе данных.

Получить переменную окружения нам поможет библиотека `python-dotenv`:
```shell
pip install python-dotenv
```

Поскольку нельзя допускать утечки `.env` файла (и других ненужных файлов) в репозиторий, был создан `.gitignore` файл, 
в котором прописаны все файлы и директории, которые нельзя загружать:
```
*.env

venv/
env/
ENV/
.venv/
```
Но для упрощения работы с приложением в будущем (вам или вашим коллегам) можно оставить `.env.example`, в котором будет храниться пример правильного env файла без чувствительных значений:
```
DB_ADMIN = postgresql://username:password@host:port/db_name
```

В файле `env.py` в папке alembic'а были внесены следующие изменения:
```python
from logging.config import fileConfig
import os

from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from sqlmodel import SQLModel
from models import *

load_dotenv()

config = context.config
if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", os.getenv("DB_ADMIN"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata
```
Здесь подгружаются переменные окружения из `.env` файла и устанавливается параметр `sqlalchemy.url` по ключу `DB_ADMIN`. Это указывает данные для подключения к базе данных, для которой будут выполняться миграции.

В файле `connection.py` аналогично параметры для соединения с базой данных берутся из переменных окружения:
```python
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DB_ADMIN')
engine = create_engine(db_url, echo=True)
```

В качестве теста в модель SkillWarriorLink был добавлен атрибут level. Для создания миграции необходимо выполнить:
```shell
alembic revision --autogenerate -m "skill added"
```

А для применения миграции нужно выполнить:
```shell
alembic upgrade head
```