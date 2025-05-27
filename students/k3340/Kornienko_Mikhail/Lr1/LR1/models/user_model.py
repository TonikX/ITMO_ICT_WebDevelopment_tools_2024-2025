from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from models.team_membership_model import TeamMembership


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    email: Optional[str] = None
    contact_number: Optional[str] = None
    is_confirmed: bool = Field(default=False)
    is_organizer: bool = Field(default=False)

    teams_created: List["Team"] = Relationship(back_populates="leader")
    teams_joined: List["Team"] = Relationship(back_populates="members", link_model=TeamMembership)
    tasks: List["Task"] = Relationship(back_populates="user")


class UserCreate(SQLModel):
    username: str
    password: str
    email: Optional[str] = None
    contact_number: Optional[str] = None


class UserSigninResponse(SQLModel):
    id: int
    username: str
    email: str
    contact_number: str
    access_token: str


class UserLogin(SQLModel):
    username: str
    password: str


class UserRead(SQLModel):
    id: int
    username: str
    email: str
    contact_number: str


class UserUpdatePassword(SQLModel):
    old_password: str
    new_password: str
