from enum import Enum
from pydantic import BaseModel
from typing import Optional, List


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
