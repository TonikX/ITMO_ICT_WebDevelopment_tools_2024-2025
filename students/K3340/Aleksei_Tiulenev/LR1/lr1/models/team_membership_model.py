from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from models.user_model import UserRead

if TYPE_CHECKING:
    from models.team_model import Team

class TeamMembership(SQLModel, table=True):
    __tablename__ = "team_memberships"

    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="teams.id", nullable=False)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    role: str = Field(nullable=False)  # например, "leader" или "member"
    join_date: Optional[str] = Field(default=None)  # Можно использовать тип datetime

    team: Optional["Team"] = Relationship(
        back_populates="members",
        sa_relationship_kwargs={"primaryjoin": "TeamMembership.team_id == Team.id"}
    )
    user: Optional["User"] = Relationship(
        back_populates="memberships",
        sa_relationship_kwargs={"primaryjoin": "TeamMembership.user_id == User.id"}
    )

# Схемы для API

class TeamMembershipCreate(SQLModel):
    team_id: int
    user_id: int
    role: str
    join_date: Optional[str] = None

class TeamMembershipRead(SQLModel):
    id: int
    team_id: int
    user: Optional[UserRead] = None
    role: str
    join_date: Optional[str]