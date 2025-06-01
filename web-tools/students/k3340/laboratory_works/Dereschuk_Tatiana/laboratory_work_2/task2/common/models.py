from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship


class ProjectRole(str, Enum):
    developer = "developer"
    designer = "designer"
    analyst = "analyst"
    manager = "manager"


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str
    password: str
    bio: Optional[str]
    created_at: datetime = datetime.now()

    skills: List["UserSkill"] = Relationship(back_populates="user")
    memberships: List["TeamMember"] = Relationship(back_populates="user")
    owned_projects: List["Project"] = Relationship(back_populates="owner")


class Skill(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None

    user_skills: List["UserSkill"] = Relationship(back_populates="skill")


class UserSkill(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    skill_id: int = Field(foreign_key="skill.id", primary_key=True)
    experience_years: Optional[int] = 0

    user: Optional[User] = Relationship(back_populates="skills")
    skill: Optional[Skill] = Relationship(back_populates="user_skills")


class Project(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    description: str
    goals: str
    expected_outcomes: str
    deadline: Optional[datetime] = None
    owner_id: int = Field(foreign_key="user.id")

    owner: Optional[User] = Relationship(back_populates="owned_projects")
    teams: List["Team"] = Relationship(back_populates="project")


class Team(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    project_id: int = Field(foreign_key="project.id")

    project: Optional[Project] = Relationship(back_populates="teams")
    members: List["TeamMember"] = Relationship(back_populates="team")


class TeamMember(SQLModel, table=True):
    team_id: int = Field(foreign_key="team.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    role: ProjectRole
    joined_at: datetime = datetime.now()

    team: Optional[Team] = Relationship(back_populates="members")
    user: Optional[User] = Relationship(back_populates="memberships")
