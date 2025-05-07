from enum import Enum
from typing import Optional, List
from pydantic import BaseModel


class Skill(BaseModel):
    id: int
    name: str
    description: str


class Profession(BaseModel):
    id: int
    title: str
    description: str


class RaceType(str, Enum):
    director = "director"
    worker = "worker"
    junior = "junior"


class Warrior(BaseModel):
    id: int
    race: RaceType
    name: str
    level: int
    profession: Optional[Profession] = None
    skills: Optional[List[Skill]] = []