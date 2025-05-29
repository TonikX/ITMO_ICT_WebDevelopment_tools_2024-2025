from datetime import date
from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class ProjectStatus(str, Enum):
    planned = "planned"
    active = "active"
    finished = "finished"


class UserDefault(SQLModel):
    name: str
    date_of_birth: date
    about: Optional[str] = ""
    phone_number: str = Field(..., min_length=11, max_length=11)
    email: str
    password: str


class User(UserDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    skills: List["UserSkill"] = Relationship(back_populates="user")
    positions: List["UserPosition"] = Relationship(back_populates="user")
    tasks: List["Task"] = Relationship(back_populates="user")
    participation: List["Participation"] = Relationship(back_populates="user")


class Skill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str


class UserSkillDefault(SQLModel):
    skill_id: int = Field(foreign_key="skill.id")
    user_id: int = Field(foreign_key="user.id")
    level: int = Field(ge=1, le=5)


class UserSkill(UserSkillDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user: Optional[User] = Relationship(back_populates="skills")
    skill: Optional[Skill] = Relationship()


class Position(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str


class UserPositionDefault(SQLModel):
    position_id: int = Field(foreign_key="position.id")
    user_id: int = Field(foreign_key="user.id")
    experience: int


class UserPosition(UserPositionDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user: Optional[User] = Relationship(back_populates="positions")
    position: Optional[Position] = Relationship()


class ProjectDefault(SQLModel):
    title: str
    description: Optional[str] = ""
    status: ProjectStatus


class Project(ProjectDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tasks: List["Task"] = Relationship(back_populates="project")
    participants: List["Participation"] = Relationship(back_populates="project")


class TaskDefault(SQLModel):
    user_id: int = Field(foreign_key="user.id")
    project_id: int = Field(foreign_key="project.id")
    description: str
    deadline: date
    status: TaskStatus


class Task(TaskDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user: Optional[User] = Relationship(back_populates="tasks")
    project: Optional[Project] = Relationship(back_populates="tasks")


class ParticipationDefault(SQLModel):
    user_id: int = Field(foreign_key="user.id")
    project_id: int = Field(foreign_key="project.id")


class Participation(ParticipationDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project: Optional[Project] = Relationship(back_populates="participants")
    user: Optional[User] = Relationship(back_populates="participation")
    description: str


class News(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    url: str
    title: str
    topic: str
    text: str
