from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.models import Priority


class TaskRead(BaseModel):
    id: int
    title: str
    description: str
    deadline: datetime
    priority: Priority
    is_completed: bool

    class Config:
        orm_mode = True


class UserWithTasks(BaseModel):
    id: int
    username: str
    tasks: List[TaskRead]

    class Config:
        orm_mode = True
