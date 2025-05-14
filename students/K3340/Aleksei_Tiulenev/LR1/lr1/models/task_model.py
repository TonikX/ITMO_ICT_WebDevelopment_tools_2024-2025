from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

if TYPE_CHECKING:
    from models.hackathon_model import Hackathon
    from models.submission_model import Submission

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    description: Optional[str] = None
    requirements: Optional[str] = None
    criteria: Optional[str] = None
    deadline: datetime = Field(nullable=False)

    hackathon_id: int = Field(foreign_key="hackathons.id", nullable=False)
    hackathon: Optional["Hackathon"] = Relationship(
        back_populates="tasks",
        sa_relationship_kwargs={"primaryjoin": "Task.hackathon_id == Hackathon.id"}
    )
    submissions: List["Submission"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={"primaryjoin": "Task.id == Submission.task_id"}
    )

# Схемы для API

class TaskCreate(SQLModel):
    title: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    criteria: Optional[str] = None
    deadline: datetime
    hackathon_id: int

class TaskRead(SQLModel):
    id: int
    title: str
    description: Optional[str]
    requirements: Optional[str]
    criteria: Optional[str]
    deadline: datetime
    hackathon_id: int