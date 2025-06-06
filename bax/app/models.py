from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Integer, ForeignKey, JSON


class Page(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(sa_column=Column(String, nullable=False))
    title: Optional[str] = None
    parsed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Role(str, Enum):
    leader = "leader"
    developer = "developer"
    designer = "designer"
    tester = "tester"


class ParserTaskResponse(SQLModel):
    task_id: str
    url: str
    status: str = "Задача начата"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(100), nullable=False))
    email: str = Field(sa_column=Column(String(100), unique=True, nullable=False))
    phone: str = Field(sa_column=Column(String(20)))

    teams: Optional[List["UserTeam"]] = Relationship(back_populates="user")


class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(100), nullable=False))
    description: str = Field(sa_column=Column(String))

    users: Optional[List["UserTeam"]] = Relationship(back_populates="team")
    works: Optional[List["Work"]] = Relationship(back_populates="team")


class UserTeam(SQLModel, table=True):
    user_id: Optional[int] = Field(
        default=None,
        foreign_key="user.id",
        primary_key=True
    )
    team_id: Optional[int] = Field(
        default=None,
        foreign_key="team.id",
        primary_key=True
    )
    role: Role = Field(sa_column=Column(String, nullable=False))

    user: Optional[User] = Relationship(back_populates="teams")
    team: Optional[Team] = Relationship(back_populates="users")


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str = Field(sa_column=Column(String))

    requirements: List[str] = Field(sa_column=Column(JSON))  # Требования к задаче
    evaluation_criteria: List[str] = Field(sa_column=Column(JSON))  # Критерии оценки

    works: Optional[List["Work"]] = Relationship(back_populates="task")


class Work(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    file: str = Field(sa_column=Column(String))  # Ссылка на файл

    task: Optional[Task] = Relationship(back_populates="works")
    team: Optional[Team] = Relationship(back_populates="works")

    evaluations: Optional[List["Evaluation"]] = Relationship(back_populates="work")


class Evaluation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    work_id: Optional[int] = Field(default=None, foreign_key="work.id")
    score: int = Field(sa_column=Column(Integer))
    feedback: str = Field(sa_column=Column(String))

    work: Optional[Work] = Relationship(back_populates="evaluations")


# DTO модели (для API)
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