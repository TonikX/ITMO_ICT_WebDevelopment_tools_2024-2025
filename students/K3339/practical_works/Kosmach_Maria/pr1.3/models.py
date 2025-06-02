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


class SkillDefault(SQLModel):
    name: Optional[str]
    description: Optional[str]


class Skill(SkillDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = ""
    warriors: Optional[List["Warrior"]] = Relationship(back_populates="skills", link_model=SkillWarriorLink)


class ProfessionDefault(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None


class Profession(ProfessionDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    description: str
    warriors_prof: List["Warrior"] = Relationship(back_populates="profession")


class WarriorDefault(SQLModel):
    race: Optional[RaceType] = None
    name: Optional[str] = None
    level: Optional[int] = None
    profession_id: Optional[int] = Field(default=None, foreign_key="profession.id")
    skill_ids: Optional[List[int]] = []


class WarriorDetails(WarriorDefault):
    profession: Optional[Profession] = None
    skills: List[SkillDefault] = []


class Warrior(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    race: RaceType
    name: str
    level: int
    profession_id: Optional[int] = Field(default=None, foreign_key="profession.id")
    profession: Optional[Profession] = Relationship(back_populates="warriors_prof")
    skills: List[Skill] = Relationship(back_populates="warriors", link_model=SkillWarriorLink)
