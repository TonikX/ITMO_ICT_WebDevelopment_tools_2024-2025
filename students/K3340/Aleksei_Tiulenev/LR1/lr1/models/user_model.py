from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.team_model import Team
    from models.team_membership_model import TeamMembership
    from models.submission_model import Submission

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    bio: Optional[str] = None

    teams_created: List["Team"] = Relationship(back_populates="creator")
    memberships: List["TeamMembership"] = Relationship(back_populates="user")
    submissions: List["Submission"] = Relationship(back_populates="user")


class UserCreate(SQLModel):
    username: str
    password: str
    email: str
    bio: Optional[str] = None

class UserLogin(SQLModel):
    username: str
    password: str

class UserRead(SQLModel):
    id: int
    username: str
    email: str
    bio: Optional[str] = None

class UserUpdatePassword(SQLModel):
    old_password: str
    new_password: str