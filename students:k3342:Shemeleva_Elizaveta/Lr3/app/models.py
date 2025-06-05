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
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

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
    notify_before_minutes: int = Field(default=60)

    task: Optional[Task] = Relationship(back_populates="notifications")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, min_length=3, max_length=50)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    roles: List["UserRole"] = Relationship(back_populates="user")

class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=20)
    description: Optional[str]

    users: List["UserRole"] = Relationship(back_populates="role")

class UserRole(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    role_id: Optional[int] = Field(default=None, foreign_key="role.id", primary_key=True)
    assigned_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="roles")
    role: Optional[Role] = Relationship(back_populates="users")
