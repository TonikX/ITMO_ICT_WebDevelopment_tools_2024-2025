from sqlmodel import SQLModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class UserRole(str, Enum):
    user = "user"
    admin = "admin"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str
    role: UserRole = Field(default=UserRole.user)


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    deadline: datetime
    priority: Priority
    is_completed: bool = False
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")


class TaskCreate(SQLModel):
    title: str
    description: str
    deadline: datetime
    priority: Priority
    is_completed: bool = False


class TimeLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[int]
    task_id: int = Field(default=None, foreign_key="task.id")


class UserTaskLink(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    task_id: int = Field(foreign_key="task.id", primary_key=True)
    role: str


class DailySchedule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime
    task_id: int = Field(foreign_key="task.id")


class ParsedRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    content_size: int
    raw: str
