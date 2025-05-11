from enum import Enum

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import date, datetime


class OrganizerBase(SQLModel):
    name: str
    email: str


class OrganizerProfile(OrganizerBase, table=True):
    __tablename__ = "organizerprofile"
    id: int = Field(default=None, primary_key=True)
    trips: List["Trip"] = Relationship(back_populates="organizer")


class OrganizerCreate(OrganizerBase):
    pass


class OrganizerRead(OrganizerBase):
    id: int


class TripBase(SQLModel):
    destination: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class Trip(TripBase, table=True):
    __tablename__ = "trip"
    id: int = Field(default=None, primary_key=True)

    organizer_profile_id: Optional[int] = Field(default=None, foreign_key="organizerprofile.id")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    user: Optional["User"] = Relationship(back_populates="trips")
    organizer: Optional["OrganizerProfile"] = Relationship(back_populates="trips")
    trip_requests: List["TripRequest"] = Relationship(back_populates="trip")
    saved_by_users: List["SavedTrip"] = Relationship(back_populates="trip")


class TripCreate(TripBase):
    organizer_profile_id: int
    user_id: Optional[int] = None


class TripRead(TripBase):
    id: int
    organizer_profile_id: Optional[int]
    user_id: Optional[int]


class UserBase(SQLModel):
    name: str
    email: str
    preferences: Optional[str] = None
    bio: Optional[str] = None


class User(UserBase, table=True):
    __tablename__ = "user"
    id: int = Field(default=None, primary_key=True)

    trips: List["Trip"] = Relationship(back_populates="user")
    trip_requests: List["TripRequest"] = Relationship(back_populates="user")
    saved_trips: List["SavedTrip"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    pass


class TripRequestStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    completed = "completed"
    cancelled = "cancelled"


class TripRequestBase(SQLModel):
    status: TripRequestStatus = Field(default=TripRequestStatus.pending)


class TripRequest(TripRequestBase, table=True):
    __tablename__ = "triprequest"
    id: int = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
    trip_id: int = Field(foreign_key="trip.id")

    user: "User" = Relationship(back_populates="trip_requests")
    trip: "Trip" = Relationship(back_populates="trip_requests")


class TripRequestCreate(TripRequestBase):
    user_id: int
    trip_id: int


class TripRequestRead(TripRequestBase):
    id: int
    user_id: int
    trip_id: int


class TripUpdate(SQLModel):
    destination: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    organizer_profile_id: Optional[int] = None
    user_id: Optional[int] = None


class SavedTripWithDetails(BaseModel):
    trip_id: int
    user_id: int
    saved_at: date
    trip: TripRead

    class Config:
        orm_mode = True


class UserRead(UserBase):
    id: int
    trips: List[TripRead]
    trip_requests: List[TripRequestRead]
    saved_trips: List[SavedTripWithDetails]


class TripRequestWithDetails(TripRequestRead):
    trip: Optional[TripRead]
    user: Optional[UserRead]


class UserUpdate(SQLModel):
    name: Optional[str] = None
    email: Optional[str] = None
    preferences: Optional[str] = None
    bio: Optional[str] = None


class TripWithDetails(TripRead):
    user: Optional[UserRead]
    organizer: Optional[OrganizerRead]


class SavedTrip(SQLModel, table=True):
    __tablename__ = "savedtrip"
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    trip_id: int = Field(foreign_key="trip.id", primary_key=True)

    saved_at: Optional[date] = Field(default_factory=date.today)

    user: "User" = Relationship(back_populates="saved_trips")
    trip: "Trip" = Relationship(back_populates="saved_by_users")


class MessageBase(BaseModel):
    content: str

    class Config:
        orm_mode = True


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="user.id")
    receiver_id: int = Field(foreign_key="user.id")
    trip_id: int = Field(foreign_key="trip.id")
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    sender: "User" = Relationship(sa_relationship_kwargs={"foreign_keys": "[Message.sender_id]"})
    receiver: "User" = Relationship(sa_relationship_kwargs={"foreign_keys": "[Message.receiver_id]"})
    trip: "Trip" = Relationship()


class MessageCreate(MessageBase):
    sender_id: int
    receiver_id: int
    trip_id: int


class MessageRead(MessageBase):
    id: int
    sender_id: int
    receiver_id: int
    trip_id: int
    timestamp: datetime


class MessageUpdate(MessageBase):
    content: Optional[str] = None


class SaveTripRequest(BaseModel):
    user_id: int
    trip_id: int


class SavedTripDelete(BaseModel):
    user_id: int
    trip_id: int
