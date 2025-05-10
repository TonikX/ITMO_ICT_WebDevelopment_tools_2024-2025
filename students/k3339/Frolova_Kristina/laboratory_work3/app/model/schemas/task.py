from typing import Optional, List

from sqlmodel import SQLModel


class TaskBase(SQLModel):
    description: str
    requirements: str
    evaluation_criteria: str

class TaskCreate(TaskBase):
    hackathon_id: int

class TaskRead(TaskBase):
    id: int
    description: str
    requirements: str
    evaluation_criteria: str
    hackathon_id: int
    hackathon: Optional['HackathonShort']


class TaskUpdate(SQLModel):
    description: Optional[str] = None
    requirements: Optional[str] = None
    evaluation_criteria: Optional[str] = None

class HackathonShort(SQLModel):
    id: int
    name: str