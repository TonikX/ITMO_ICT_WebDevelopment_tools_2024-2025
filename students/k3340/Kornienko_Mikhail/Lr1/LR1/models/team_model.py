from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

from models.team_membership_model import TeamMembership
from models.user_model import UserRead


class TeamDefault(SQLModel):
    name: str
    description: Optional[str] = None


class Team(TeamDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    leader_id: int = Field(foreign_key="user.id")

    leader: Optional["User"] = Relationship(back_populates="teams_created")
    members: Optional[List["User"]] = Relationship(back_populates="teams_joined", link_model=TeamMembership)
    submissions: Optional[List["Submission"]] = Relationship(back_populates="team")

class TeamWithFullDetails(TeamDefault):
    id: int
    leader: Optional[UserRead] = None
    members: List[UserRead] = []


class TeamCreate(SQLModel):
    name: str
    description: Optional[str] = None


class TeamUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
