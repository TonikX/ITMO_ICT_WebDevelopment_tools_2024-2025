# models.py

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel


class RaceType(Enum):
    director = "director"
    worker = "worker"
    junior = "junior"

# Модель профессии
class Profession(BaseModel):
    id: int
    title: str
    description: str

# Модель умения
class Skill(BaseModel):
    id: int
    name: str
    description: str

# Модель воина с вложенной моделью профессии и списком умений
class Warrior(BaseModel):
    id: int
    race: RaceType
    name: str
    level: int
    profession: Profession
    skills: Optional[List[Skill]] = []
