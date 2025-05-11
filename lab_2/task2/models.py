from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship



class UserRole(Enum):
    user = "user"
    admin = "admin"

class PriorityLevel(Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"



class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: EmailStr
    password: str
    phone: str
    role: UserRole = UserRole.user

    tasks: List["Task"] = Relationship(back_populates="owner")


class TaskTag(SQLModel, table=True):
    task_id: int = Field(foreign_key="task.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)
    relevance: Optional[str] = "general"


class Tag(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    tasks: List["Task"] = Relationship(back_populates="tags", link_model=TaskTag)


class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: PriorityLevel = PriorityLevel.medium
    owner_id: int = Field(foreign_key="user.id")

    owner: Optional[User] = Relationship(back_populates="tasks")
    tags: List[Tag] = Relationship(back_populates="tasks", link_model=TaskTag)
    time_logs: List["TimeLog"] = Relationship(back_populates="task")


class TimeLog(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    start_time: datetime
    end_time: Optional[datetime] = None

    task: Optional[Task] = Relationship(back_populates="time_logs")





