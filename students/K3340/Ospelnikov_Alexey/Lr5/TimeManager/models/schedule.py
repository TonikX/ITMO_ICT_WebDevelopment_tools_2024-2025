from typing import Optional, List
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship, Column, TIMESTAMP, text
from .task_schedule import TaskSchedule


class Schedule(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    date: datetime
    tasks: Optional[List["Task"]] = Relationship(
        back_populates="schedules", link_model=TaskSchedule
    )
    productivity_score: Optional[int] = 5
    notes: Optional[str] = ''
    schedule_link: List[TaskSchedule] = Relationship(back_populates="schedules")