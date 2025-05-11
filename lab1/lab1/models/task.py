from typing import Optional, List
from sqlmodel import SQLModel, Field
from models.models import PriorityLevel


class TaskCreate(SQLModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[str] = None
    priority: PriorityLevel = PriorityLevel.medium
    tag_ids: Optional[List[int]] = []


class TaskRead(SQLModel):
    id: int
    title: str
    description: Optional[str]
    deadline: Optional[str]
    priority: PriorityLevel
    owner_id: int
