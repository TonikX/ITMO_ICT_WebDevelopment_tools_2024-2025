from datetime import date
from enum import StrEnum
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel
from core.models import CoreModel
from teams.models import Team
from users.models import User


class ProjectStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_DEVELOPMENT = "in_development"
    FROZEN = "frozen"


class Workflow(SQLModel, table=True):
    team_id: int = Field(
        foreign_key="team.id",
        primary_key=True,
        ondelete="CASCADE",
    )

    project_id: int = Field(
        foreign_key="project.id",
        primary_key=True,
        ondelete="CASCADE",
    )


class Project(CoreModel, table=True):
    name: str
    description: str = Field(max_length=500, default="")
    deadline: Optional[date] = Field(default=None)

    owner_id: int = Field(
        foreign_key="user.id",
        nullable=False,
        ondelete="CASCADE",
    )

    owner: Optional[User] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"},
    )

    teams: Optional[list[Team]] = Relationship(
        link_model=Workflow,
        sa_relationship_kwargs={"lazy": "selectin", "uselist": True},
    )
