from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class RaceType(str, Enum):
    director = "director"
    worker = "worker"
    junior = "junior"

# Ассоциативная таблица для связи многие-ко-многим
class SkillWarriorLink(SQLModel, table=True):
    skill_id: Optional[int] = Field(
        default=None, foreign_key="skill.id", primary_key=True
    )
    warrior_id: Optional[int] = Field(
        default=None, foreign_key="warrior.id", primary_key=True
    )

# Базовые модели без связей (для запросов)
class SkillDefault(SQLModel):
    name: str
    description: Optional[str] = ""

class ProfessionDefault(SQLModel):
    title: str
    description: str

class WarriorDefault(SQLModel):
    race: RaceType
    name: str
    level: int
    profession_id: Optional[int] = Field(default=None, foreign_key="profession.id")

# Основные модели с таблицами и связями
class Skill(SkillDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    warriors: List["Warrior"] = Relationship(back_populates="skills", link_model=SkillWarriorLink)

class Profession(ProfessionDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    warriors: List["Warrior"] = Relationship(back_populates="profession")

class Warrior(WarriorDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profession: Optional[Profession] = Relationship(back_populates="warriors")
    skills: Optional[List[Skill]] = Relationship(back_populates="warriors", link_model=SkillWarriorLink)

# Модели для ответов с вложенными объектами
class WarriorProfessions(WarriorDefault):
    profession: Optional[Profession] = None

class WarriorSkills(SQLModel):
    skills: Optional[List[Skill]] = None

class WarriorFull(WarriorProfessions, WarriorSkills):
    pass