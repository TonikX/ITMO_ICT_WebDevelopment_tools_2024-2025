from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from models.team_model import Team
from models.task_model import Task


class SubmissionDefault(SQLModel):
    description: str
    submission_url: Optional[str] = None


class Submission(SubmissionDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="team.id")
    task_id: int = Field(foreign_key="task.id")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    score: Optional[float] = None

    team: Optional["Team"] = Relationship(back_populates="submissions")
    task: Optional["Task"] = Relationship(back_populates="submissions")


class SubmissionWithFullDetails(SubmissionDefault):
    id: int
    submitted_at: datetime
    score: Optional[float] = None
    team: Optional[Team] = None
    task: Optional[Task] = None


class SubmissionCreate(SQLModel):
    description: str
    submission_url: Optional[str] = None
    team_id: int
    task_id: int


class SubmissionUpdate(SQLModel):
    description: Optional[str] = None
    submission_url: Optional[str] = None
    score: Optional[float] = None

