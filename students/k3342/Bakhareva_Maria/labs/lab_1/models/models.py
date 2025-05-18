from enum import Enum
from datetime import datetime
from typing import Optional, List

from pydantic import EmailStr, BaseModel
from sqlmodel import SQLModel, Field, Relationship


class JourneyStatus(str, Enum):
    planned = "planned"
    active = "in_progress"
    finished = "completed"
    aborted = "canceled"


class TransportType(str, Enum):
    car = "car"
    bike = "bicycle"
    plane = "plane"
    walk = "walking"
    train = "train"
    boat = "boat"
    bus = "bus"
    scooter = "scooter"
    moto = "motorcycle"


class RoleType(str, Enum):
    user = "user"
    admin = "admin"


class ParticipationStatus(str, Enum):
    accepted = "confirmed"
    pending = "pending"
    declined = "declined"
    left = "canceled"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    profile_image: Optional[str] = None
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    role: RoleType = Field(default=RoleType.user)

    journeys_created: List["Journey"] = Relationship(back_populates="creator")

class UserUpdate(BaseModel):
    full_name: Optional[str]
    phone_number: Optional[str]
    profile_image: Optional[str]

class Journey(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    creator_id: int = Field(foreign_key="user.id")
    title: Optional[str] = None
    notes: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    transport: Optional[TransportType] = None
    status: JourneyStatus = Field(default=JourneyStatus.planned)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    creator: Optional[User] = Relationship(back_populates="journeys_created")
    participants: List["Participant"] = Relationship(back_populates="journey")
    messages: List["Message"] = Relationship(back_populates="journey")
    stops: List["JourneyStop"] = Relationship(back_populates="journey")


class Participant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    journey_id: int = Field(foreign_key="journey.id")
    user_id: int = Field(foreign_key="user.id")
    status: ParticipationStatus = Field(default=ParticipationStatus.pending)
    added_at: datetime = Field(default_factory=datetime.utcnow)

    journey: Journey = Relationship(back_populates="participants")
    user: User = Relationship()


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    journey_id: int = Field(foreign_key="journey.id")
    sender_id: int = Field(foreign_key="user.id")
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    journey: Journey = Relationship(back_populates="messages")
    sender: User = Relationship()


class JourneyStop(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    journey_id: int = Field(foreign_key="journey.id")
    location: str
    order: int
    arrival_time: Optional[datetime] = None
    departure_time: Optional[datetime] = None
    created_on: datetime = Field(default_factory=datetime.utcnow)

    journey: Journey = Relationship(back_populates="stops")

class UserPublic(BaseModel):
    id: Optional[int]
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    profile_image: Optional[str] = None
    role: RoleType

    class Config:
        from_attributes = True


class ParticipantPublic(BaseModel):
    id: Optional[int]
    status: ParticipationStatus
    added_at: datetime
    user: Optional[UserPublic] = None


class JourneyWithParticipants(BaseModel):
    id: Optional[int]
    title: Optional[str]
    notes: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    transport: Optional[TransportType]
    status: JourneyStatus
    created_at: datetime
    creator: UserPublic
    participants: List[ParticipantPublic] = []

    class Config:
        from_attributes = True