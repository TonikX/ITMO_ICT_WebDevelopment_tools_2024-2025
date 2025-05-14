from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

if TYPE_CHECKING:
    from models.task_model import Task
    from models.user_model import User
    from models.team_model import Team

class Submission(SQLModel, table=True):
    __tablename__ = "submissions"

    id: Optional[int] = Field(default=None, primary_key=True)
    description: Optional[str] = Field(default=None)
    file_url: str = Field(nullable=False)
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    evaluation: Optional[float] = None

    task_id: int = Field(foreign_key="tasks.id", nullable=False)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    team_id: Optional[int] = Field(default=None, foreign_key="teams.id")

    task: Optional["Task"] = Relationship(
        back_populates="submissions",
        sa_relationship_kwargs={"primaryjoin": "Submission.task_id == Task.id"}
    )
    user: Optional["User"] = Relationship(
        sa_relationship_kwargs={"primaryjoin": "Submission.user_id == User.id"}
    )
    team: Optional["Team"] = Relationship(
        sa_relationship_kwargs={"primaryjoin": "Submission.team_id == Team.id"}
    )

# Схемы для API

class SubmissionCreate(SQLModel):
    description: Optional[str] = None
    file_url: str
    task_id: int
    user_id: Optional[int] = None
    team_id: Optional[int] = None

class SubmissionRead(SQLModel):
    id: int
    description: Optional[str]
    file_url: str
    submitted_at: datetime
    evaluation: Optional[float]
    task_id: int
    user_id: Optional[int]
    team_id: Optional[int]