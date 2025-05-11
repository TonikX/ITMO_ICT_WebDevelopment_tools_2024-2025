from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from models.user_model import UserRead


class TaskDefault(SQLModel):
    title: str
    description: str
    requirements: str
    evaluation_criteria: str


class Task(TaskDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="tasks")
    submissions: Optional[List["Submission"]] = Relationship(back_populates="task")


class TaskWithFullDetails(TaskDefault):
    id: int
    created_at: datetime
    user: Optional[UserRead] = None


class TaskCreate(SQLModel):
    title: str
    description: str
    requirements: str
    evaluation_criteria: str


class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    evaluation_criteria: Optional[str] = None
