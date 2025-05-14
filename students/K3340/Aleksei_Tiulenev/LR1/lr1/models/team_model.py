from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from models.user_model import UserRead
from models.team_membership_model import TeamMembership, TeamMembershipRead

if TYPE_CHECKING:
    from models.user_model import User

class Team(SQLModel, table=True):
    __tablename__ = "teams"

    id: Optional[int] = Field(default=None, primary_key=True)
    team_name: str = Field(index=True, unique=True, nullable=False)
    description: Optional[str] = None
    creator_id: int = Field(foreign_key="users.id", nullable=False)

    creator: Optional["User"] = Relationship(
        back_populates="teams_created",
        sa_relationship_kwargs={"primaryjoin": "Team.creator_id == User.id"}
    )
    members: List["TeamMembership"] = Relationship(
        back_populates="team",
        sa_relationship_kwargs={"primaryjoin": "Team.id == TeamMembership.team_id"}
    )

# Схемы для API

class TeamCreate(SQLModel):
    team_name: str
    description: Optional[str] = None

class TeamRead(SQLModel):
    id: int
    team_name: str
    description: Optional[str]
    creator: Optional[UserRead] = None
    members: List[TeamMembershipRead] = []