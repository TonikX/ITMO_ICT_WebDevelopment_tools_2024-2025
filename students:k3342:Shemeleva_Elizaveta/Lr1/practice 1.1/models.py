from enum import Enum
from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskBase(BaseModel):
    description: str = Field(..., example="Написать отчет по практике")
    due_date: datetime = Field(..., example="2025-05-30T18:00:00")
    priority: Priority = Field(..., example="high")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[Priority] = None
    spent_time: Optional[float] = Field(None, example=1.25)


class Task(TaskBase):
    id: int
    spent_time: float = Field(0.0, example=0.0)

    class Config:
        orm_mode = True
