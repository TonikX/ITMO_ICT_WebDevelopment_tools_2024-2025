from typing import List, Optional
from pydantic import BaseModel
from models import RaceType


class SkillRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = ""

    class Config:
        orm_mode = True


class ProfessionRead(BaseModel):
    id: int
    title: str
    description: str

    class Config:
        orm_mode = True


class WarriorRead(BaseModel):
    id: int
    name: str
    race: RaceType
    level: int
    profession: Optional[ProfessionRead]
    skills: List[SkillRead] = []

    class Config:
        orm_mode = True


class WarriorCreate(BaseModel):
    name: str
    race: RaceType
    level: int
    profession_id: Optional[int] = None
    skill_ids: List[int] = []


class SkillCreate(BaseModel):
    name: str
    description: Optional[str] = ""