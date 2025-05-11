import enum
import uuid
from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Enum as SAEnum


class TripRole(str, enum.Enum):
    passenger = "passenger"
    organizer = "organizer"

class TripStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    declined = "declined"


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    username: str = Field(index=True, unique=True, nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    is_admin: bool = Field(default=False)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    age: Optional[int] = Field(default=None)
    description: Optional[str] = Field(default=None)
    password_hash: str

    created_trips: List["Trip"] = Relationship(back_populates="creator")
    trip_participations: List["TripParticipation"] = Relationship(back_populates="user")
    user_skills: List["UserSkill"] = Relationship(back_populates="user")

class Trip(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    title: str
    description: str
    departure: datetime
    arrival: Optional[datetime] = None
    departure_location: str
    arrival_location: str
    creator_id: uuid.UUID = Field(foreign_key="user.id")

    creator: Optional[User] = Relationship(back_populates="created_trips")
    participations: List["TripParticipation"] = Relationship(back_populates="trip")

class TripParticipation(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    trip_id: uuid.UUID = Field(foreign_key="trip.id")
    role: TripRole = Field(
        default=TripRole.passenger,
        sa_column=Column(SAEnum(TripRole, name="trip_role", create_type=True), default=TripRole.passenger)
    )
    status: TripStatus = Field(
        default=TripStatus.pending,
        sa_column=Column(SAEnum(TripStatus, name="trip_status", create_type=True), default=TripStatus.pending)
    )
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="trip_participations")
    trip: Optional[Trip] = Relationship(back_populates="participations")

class Skill(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str
    description: Optional[str] = None
    user_skills: List["UserSkill"] = Relationship(back_populates="skill")

class UserSkill(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    skill_id: uuid.UUID = Field(foreign_key="skill.id")
    proficiency: int = Field(default=1, ge=1, le=10)

    user: Optional[User] = Relationship(back_populates="user_skills")
    skill: Optional[Skill] = Relationship(back_populates="user_skills")
