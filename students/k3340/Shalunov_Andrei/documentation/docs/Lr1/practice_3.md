# Практика 1.3 — Миграции, ENV, GitIgnore и структура проекта

## Файл .gitignore
```
.idea
.env
.venv/
__pycache__/
*.py[cod]
*.swp
.idea/
.vscode/
.ipynb_checkpoints/
*.log

# vim temporary files
*~
.*.sw?
.cache
```

## connection.py
```
import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine

# 1. Загрузка .env
load_dotenv()

# 2. Чтение URL из переменной окружения
DB_URL = os.getenv("DB_ADMIN")
engine = create_engine(DB_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

```

## models.py
```
from enum import Enum
from typing import Optional, List
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
    level: int | None


class SkillBase(SQLModel):
    name: str
    description: Optional[str] = ""


class Skill(SkillBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    warriors: List["Warrior"] = Relationship(back_populates="skills", link_model=SkillWarriorLink)


class ProfessionBase(SQLModel):
    title: str
    description: str


class Profession(ProfessionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    warriors_prof: List["Warrior"] = Relationship(back_populates="profession")


class WarriorBase(SQLModel):
    race: RaceType
    name: str
    level: int
    profession_id: Optional[int] = Field(default=None, foreign_key="profession.id")


class Warrior(WarriorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profession: Optional[Profession] = Relationship(back_populates="warriors_prof")
    skills: Optional[List[Skill]] = Relationship(back_populates="warriors", link_model=SkillWarriorLink)


class WarriorWithProfession(WarriorBase):
    id: int
    profession: Optional[Profession] = None


class WarriorWithFullDetails(WarriorWithProfession):
    skills: List[Skill] = []
```

## Генерация и применение миграций
```
alembic revision --autogenerate -m "initial schema"
alembic upgrade head

alembic revision --autogenerate -m "add level to SkillWarriorLink"
alembic upgrade head

```