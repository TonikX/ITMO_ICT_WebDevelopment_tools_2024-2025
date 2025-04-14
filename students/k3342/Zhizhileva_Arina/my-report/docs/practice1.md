## Практика

### Практика 1.1. Создание базового приложения на FastAPI

Установка FastApi с cопутствующими библиотеками в командной строке с помощью команды:

pip install fastapi[all]

**по пути 127.0.0.1:8000**
![](images/1.png)
**по пути 127.0.0.1:8000/docs**
![](images/2.png)
![](images/3.png)
**Запрос всех воинов:**
![](images/4.png)
**Добавление воина:**
![](images/5.png)
**Удаление воина:**
![](images/6.png)
**Редактирование воина:**
![](images/7.png)
**После обновления кода для представлений изменилась документация к разработанному API (127.0.0.1:8000/docs). Теперь для каждого запроса отображается описание в каком формате передаются и принимаются данные для каждого реализованного метода.**
![](images/8.png)
![](images/9.png)
![](images/10.png)
![](images/11.png)


### Практика 1.2. Настройка БД, SQLModel и миграции через Alembic

pip install sqlmodel

**код из файла db.py:**
```python
from sqlmodel import SQLModel, Session, create_engine

db_url = 'postgresql://postgres:Arina2992@localhost:5432/warriors_db'
engine = create_engine(db_url, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

```

**код из файла models.py:**
```python
from enum import Enum
from typing import Optional, List

#from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship


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


class Skill(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = ""
    warriors: Optional[List["Warrior"]] = Relationship(back_populates="skills", link_model=SkillWarriorLink)


class Profession(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    description: str
    warriors_prof: List["Warrior"] = Relationship(back_populates="profession")


class Warrior(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    race: RaceType
    name: str
    level: int
    profession_id: Optional[int] = Field(default=None, foreign_key="profession.id")
    profession: Optional[Profession] = Relationship(back_populates="warriors_prof")
    skills: Optional[List[Skill]] = Relationship(back_populates="warriors", link_model=SkillWarriorLink)

```
Чтобы описанные таблицы были созданы необходимо добавить в main.py специальный метод on_startup с декоратором on_event вызывающий внутри их инициализацию. 

```python
@app.on_event("startup")
def on_startup():
    init_db()

```
После запуска приложения в консоли вывелся SQL-запрос на создание сущностей, описанных в models.py

```sq
CREATE TABLE skill (
        id SERIAL NOT NULL,
        name VARCHAR NOT NULL,
        description VARCHAR,
        PRIMARY KEY (id)
)

CREATE TABLE profession (
        id SERIAL NOT NULL,
        title VARCHAR NOT NULL,
        description VARCHAR NOT NULL,
        PRIMARY KEY (id)
)

CREATE TABLE warrior (
        id SERIAL NOT NULL,
        race racetype NOT NULL,
        name VARCHAR NOT NULL,
        level INTEGER NOT NULL,
        profession_id INTEGER,
        PRIMARY KEY (id),
        FOREIGN KEY(profession_id) REFERENCES profession (id)
)

CREATE TABLE skillwarriorlink (
        skill_id INTEGER NOT NULL,
        warrior_id INTEGER NOT NULL,
        PRIMARY KEY (skill_id, warrior_id),
        FOREIGN KEY(skill_id) REFERENCES skill (id),
        FOREIGN KEY(warrior_id) REFERENCES warrior (id)
)

```

### Практика 1.3. Миграции, ENV, GitIgnore и структура проекта

Для интеграции Alembic в разрабатываемый проект необходимо его установить через пакетный менеджер: 

pip install alembic  

Реализация механизма миграций происходит через вызов alembic init [name] в командной строке, где [name] — название папки, хранящей настройки миграций. Сгенерируем папку с миграциями и сопутствующие файлы настроек:

alembic init migrations 

В корне проекта, помимо ранее созданных файлов должна сформироваться следующая структура
![](images/structure.png)

Сгенерировалась папка migratgions хранящая внутри себя папку с файлами миграций versions, файл окружения БД env.py и шаблон генерации миграций script.py.mako. В корне проекта добавился файл настроек alembic.ini

**код из файла env.py:**
```python
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from models import *

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
#target_metadata = None

target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

```