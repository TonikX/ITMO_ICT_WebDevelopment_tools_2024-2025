import datetime
from enum import Enum
from typing import Optional, List

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship


class UserRole(Enum):
    user = "user"
    admin = "admin"

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: EmailStr
    password: str
    phone: str
    role: UserRole = UserRole.user

class PriorityLevel(Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    deadline: Optional[str] = None  # или datetime
    priority: PriorityLevel = PriorityLevel.medium
    owner_id: int = Field(foreign_key="user.id")

    owner: Optional[User] = Relationship(back_populates="tasks")
    tags: list["Tag"] = Relationship(back_populates="tasks", link_model="TaskTag")
    time_logs: list["TimeLog"] = Relationship(back_populates="task")


class Tag(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    tasks: list["Task"] = Relationship(back_populates="tags", link_model="TaskTag")


class TaskTag(SQLModel, table=True):
    task_id: int = Field(foreign_key="task.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)
    relevance: Optional[str] = "general"  # Дополнительное поле


class TimeLog(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    start_time: str  # или datetime
    end_time: Optional[str] = None

    task: Optional[Task] = Relationship(back_populates="time_logs")



class TaskDefault(SQLModel):
    title: str
    description: Optional[str] = ""
    priority: PriorityEnum
    deadline: Optional[str] = None
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")


class Task(TaskDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user: Optional[User] = Relationship(back_populates="tasks")


class TaskWithUser(TaskDefault):
    user: Optional[User] = None

class TaskRead(TaskDefault):
    id: int

    class Config:
        from_orm = True

