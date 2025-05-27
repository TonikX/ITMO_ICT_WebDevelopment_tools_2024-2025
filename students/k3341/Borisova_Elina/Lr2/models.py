from enum import Enum
from typing import Optional, List

from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.dialects.postgresql import JSON

class Role(str, Enum):
    leader = "leader"
    developer = "developer"
    designer = "designer"
    tester = "tester"

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True)
    phone: str
    skills: str
    teams: Optional[List["UserTeam"]] = Relationship(back_populates="user")

class Team(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    description: str
    users: Optional[List["UserTeam"]] = Relationship(back_populates="team")
    works: Optional[List["Work"]] = Relationship(back_populates="team")


class UserTeam(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    team_id: Optional[int] = Field(default=None, foreign_key="team.id", primary_key=True)
    role: Role

    user: Optional[User] = Relationship(back_populates="teams")
    team: Optional[Team] = Relationship(back_populates="users")


class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    description: str
    requirements: List[str] = Field(sa_type=JSON)
    evaluation_criteria: List[str] = Field(sa_type=JSON)
    works: Optional[List["Work"]] = Relationship(back_populates="task")

class Work(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    file: str

    task: Optional[Task] = Relationship(back_populates="works")
    team: Optional[Team] = Relationship(back_populates="works")
    evaluations: Optional[List["Evaluation"]] = Relationship(back_populates="work")

class Evaluation(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    work_id: Optional[int] = Field(default=None, foreign_key="work.id")  # Ссылка на работу
    score: int
    feedback: str
    work: Optional[Work] = Relationship(back_populates="evaluations")

class UserDefault(SQLModel):
    name: str
    email: str
    phone: str

class TeamDefault(SQLModel):
    name: str
    description: str

class TaskDefault(SQLModel):
    description: str
    requirements: List[str]
    evaluation_criteria: List[str]

class WorkDefault(SQLModel):
    task_id: int
    team_id: int
    file: str

class EvaluationDefault(SQLModel):
    work_id: int
    score: int
    feedback: str

class Page(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    title: Optional[str] = None
    parsed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))