from datetime import datetime, date, time
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    password: str

    tasks: List["Task"] = Relationship(back_populates="owner")
    schedules: List["DailySchedule"] = Relationship(back_populates="user")


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Priority = Priority.medium

    owner: Optional[User] = Relationship(back_populates="tasks")
    time_logs: List["TimeLog"] = Relationship(back_populates="task")
    schedule_items: List["ScheduleTask"] = Relationship(back_populates="task")


class TimeLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None

    task: Optional[Task] = Relationship(back_populates="time_logs")


class DailySchedule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    date: date

    user: Optional[User] = Relationship(back_populates="schedules")
    items: List["ScheduleTask"] = Relationship(back_populates="schedule")


class ScheduleTask(SQLModel, table=True):
    schedule_id: int = Field(foreign_key="dailyschedule.id", primary_key=True)
    task_id: int = Field(foreign_key="task.id", primary_key=True)
    planned_time: Optional[time] = None

    schedule: Optional[DailySchedule] = Relationship(back_populates="items")
    task: Optional[Task] = Relationship(back_populates="schedule_items")
