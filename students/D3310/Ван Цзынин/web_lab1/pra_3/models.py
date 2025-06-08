from sqlmodel import SQLModel, Field
from typing import Optional, List


class SkillWarriorLink(SQLModel, table=True):
    skill_id: Optional[int] = Field(
        default=None, foreign_key="skill.id", primary_key=True
    )
    warrior_id: Optional[int] = Field(
        default=None, foreign_key="warrior.id", primary_key=True
    )
    level: Optional[int]


class Skill(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = ""
    warriors: Optional[List["Warrior"]] = []


class Warrior(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    race: str
    name: str
    level: int
    skills: Optional[List[Skill]] = []