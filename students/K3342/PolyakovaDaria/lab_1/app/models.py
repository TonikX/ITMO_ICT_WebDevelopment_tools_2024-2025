from __future__ import annotations
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import Mapped
from datetime import datetime
from enum import Enum


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class UserRole(str, Enum):
    user = "user"
    admin = "admin"


class UserTaskLink(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    task_id: int = Field(foreign_key="task.id", primary_key=True)
    role: str


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str
    role: UserRole = Field(default=UserRole.user)

    tasks: Mapped[List["Task"]] = relationship(back_populates="users", link_model=UserTaskLink)


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    deadline: datetime
    priority: Priority
    is_completed: bool = False

    users: Mapped[List[User]] = relationship(back_populates="tasks", link_model=UserTaskLink)


class TimeLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[int]
    task_id: int = Field(default=None, foreign_key="task.id")


class DailySchedule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime
    task_id: int = Field(foreign_key="task.id")


class TaskCreate(BaseModel):
    title: str
    description: str
    deadline: datetime
    priority: Priority
    is_completed: bool = False
