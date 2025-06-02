from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from model.models.models import Priority, User


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[Priority] = Priority.medium


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[Priority] = None


class TaskRead(TaskBase):
    id: int
    owner: Optional["User"] = None

class TaskReadShort(BaseModel):
    id: int
    title: str
    deadline: Optional[datetime] = None
    priority: Priority