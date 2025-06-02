from datetime import datetime
from typing import Optional
from models.task import *
from pydantic import BaseModel, EmailStr


class TaskCreate(BaseModel):
    id: int
    name: str
    description: str

class TaskRead(BaseModel):
    id: int
    name: str
    description: str
    deadline: datetime
    status: StatusType
    priority: PriorityType
    created_by: int

    class Config:
        orm_mode = True