from datetime import date, datetime, timezone
from enum import StrEnum
from typing import Optional

from sqlmodel import Field, Relationship
from core.models import CoreModel
from users.models import User


class Role(StrEnum):
    OWNER = "owner"
    TEAMLEAD = "teamlead"
    PROGRAMMER = "programmer"
    TESTER = "tester"
    MANAGER = "manager"


class TaskStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"


class Team(CoreModel, table=True):
    name: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )


class Member(CoreModel, table=True):
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    team_id: int = Field(foreign_key="team.id", ondelete="CASCADE")
    role: Role

    user: User = Relationship(
        sa_relationship_kwargs={"lazy": "joined"},
    )


class Task(CoreModel, table=True):
    member_id: Optional[int] = Field(
        foreign_key="member.id",
        nullable=True,
        ondelete="SET NULL",
    )

    member: Member = Relationship(
        sa_relationship_kwargs={"lazy": "joined"},
    )

    description: str = Field(max_length=500, default="")
    status: TaskStatus = Field(default=TaskStatus.NOT_STARTED)
    deadline: Optional[date] = Field(nullable=True)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
