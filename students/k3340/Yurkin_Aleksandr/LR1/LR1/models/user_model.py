from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

from models.trip_participant_model import TripParticipant


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    bio: Optional[str] = None
    experience: Optional[str] = None
    preferences: Optional[str] = None

    trips_created: List["Trip"] = Relationship(back_populates="creator")
    trips_joined: List["Trip"] = Relationship(back_populates="participants", link_model=TripParticipant)
    reviews: List["Review"] = Relationship(back_populates="user")
    messages: List["Message"] = Relationship(back_populates="user")


class UserCreate(SQLModel):
    username: str
    password: str
    bio: Optional[str] = None
    experience: Optional[str] = None
    preferences: Optional[str] = None

class UserLogin(SQLModel):
    username: str
    password: str

class UserRead(SQLModel):
    id: int
    username: str
    bio: Optional[str] = None
    experience: Optional[str] = None
    preferences: Optional[str] = None

class UserUpdatePassword(SQLModel):
    old_password: str
    new_password: str
