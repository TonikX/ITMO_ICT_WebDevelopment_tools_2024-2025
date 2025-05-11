from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import validator
from sqlalchemy import DateTime
from sqlmodel import SQLModel, Field, Relationship, Column, JSON

class Role(str, Enum):
    organizer = "Организатор"
    participant = "Участник"

class Participant(SQLModel, table=True):
    participant_id: int = Field(default=None, primary_key=True)
    trip_id: int = Field(default=None, foreign_key="trip.trip_id")
    user_id: int = Field(default=None, foreign_key="user.user_id")
    role: Role

    trip: "Trip" = Relationship(back_populates="participants")
    user: "User" = Relationship(back_populates="trips")

class ParticipantCreate(SQLModel):
    trip_id: int
    user_id: int
    role: Role

class User(SQLModel, table=True):
    user_id: int = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str
    full_name: str
    bio: Optional[str] = None
    skills: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    preferences: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))

    trips: List["Participant"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True
        }
    )
    reviews: List["Review"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True
        }
    )
    discussions: List["Discussion"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True
        }
    )

class UserCreate(SQLModel):
    username: str
    email: str
    password: str
    full_name: str
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    preferences: Optional[List[str]] = None

class UserLogin(SQLModel):
    username: str
    password: str

class UserUpdatePassword(SQLModel):
    current_password: str
    new_password: str

class Review(SQLModel, table=True):
    review_id: int = Field(default=None, primary_key=True)
    trip_id: int = Field(default=None, foreign_key="trip.trip_id")
    user_id: int = Field(default=None, foreign_key="user.user_id")
    rating: int
    comment: str

    trip: "Trip" = Relationship(back_populates="reviews")
    user: User = Relationship(back_populates="reviews")


class ReviewCreate(SQLModel):
    trip_id: int
    user_id: int
    rating: int = Field(..., ge=1, le=5, description="Рейтинг должен быть от 1 до 5")
    comment: str

class Discussion(SQLModel, table=True):
    discussion_id: int = Field(default=None, primary_key=True)
    trip_id: int = Field(default=None, foreign_key="trip.trip_id")
    user_id: int = Field(default=None, foreign_key="user.user_id")
    sent_at: datetime = Field(
        sa_column=Column(DateTime(timezone=False)),
        default_factory=datetime.utcnow
    )
    message: str

    trip: "Trip" = Relationship(back_populates="discussions")
    user: User = Relationship(back_populates="discussions")

class DiscussionCreate(SQLModel):
    trip_id: int
    message: str

    model_config = {
        "from_attributes": True
    }


class DiscussionUpdate(SQLModel):
    trip_id: Optional[int]
    message: Optional[str]
    model_config = {
        "from_attributes": True
    }

class Trip(SQLModel, table=True):
    trip_id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.user_id")
    title: str
    description: str
    start_date: datetime = Field(sa_column=Column(DateTime()))
    end_date: datetime = Field(sa_column=Column(DateTime()))
    start_place: str
    destination: str
    status: str

    participants: List[Participant] = Relationship(
        back_populates="trip",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True
        }
    )
    reviews: List[Review] = Relationship(
        back_populates="trip",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True
        }
    )
    discussions: List[Discussion] = Relationship(
        back_populates="trip",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True
        }
    )

class TripCreate(SQLModel):
    user_id: int
    title: str
    description: str
    start_date: datetime
    end_date: datetime
    start_place: str
    destination: str
    status: str
    @validator("start_date", "end_date", pre=True)
    def parse_datetime(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%dT%H:%M")
            except ValueError:
                raise ValueError("Формат даты должен быть YYYY-MM-DDTHH:MM")
        return v

class TripUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    start_place: Optional[str] = None
    destination: Optional[str] = None
    status: Optional[str] = None
    @validator("start_date", "end_date", pre=True)
    def parse_datetime(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%dT%H:%M")
            except ValueError:
                raise ValueError("Формат даты должен быть YYYY-MM-DDTHH:MM")
        return v


class UserBase(SQLModel):
    username: str

    class Config:
        from_attributes = True


class ParticipantOut(SQLModel):
    role: Role
    user: UserBase

    class Config:
        from_attributes = True


class ReviewOut(SQLModel):
    rating: int
    comment: str
    user: UserBase

    class Config:
        from_attributes = True


class DiscussionOut(SQLModel):
    message: str
    sent_at: datetime
    user: UserBase

    class Config:
        from_attributes = True

class TripOut(SQLModel):
    trip_id: int
    user_id: int
    title: str
    description: str
    start_date: datetime
    end_date: datetime
    start_place: str
    destination: str
    status: str
    participants: List[ParticipantOut] = []
    reviews: List[ReviewOut] = []
    discussions: List[DiscussionOut] = []

    class Config:
        from_attributes = True