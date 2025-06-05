from enum import Enum
from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship


class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str
    due_date: datetime
    priority: PriorityEnum
    spent_time: float = 0.0

    time_entries: List["TimeEntry"] = Relationship(back_populates="task")
    notifications: List["Notification"] = Relationship(back_populates="task")


class TimeEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    start_at: datetime
    end_at: datetime
    duration: float

    task: Optional[Task] = Relationship(back_populates="time_entries")


class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    notify_before_minutes: int = 60

    task: Optional[Task] = Relationship(back_populates="notifications")
