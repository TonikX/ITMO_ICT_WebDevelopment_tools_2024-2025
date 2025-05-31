from enum import Enum
import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel, Field, Relationship
from sqlmodel import Field


class TripStatus(str, Enum):
    planned = "planned"
    in_progress = "in_progress"
    completed = "completed"
    canceled = "canceled"


class VehicleType(str, Enum):
    car = "car"
    motorcycle = "motorcycle"
    bicycle = "bicycle"
    scooter = "scooter"
    train = "train"
    bus = "bus"
    plane = "plane"
    boat = "boat"
    walking = "walking"


class CompanionStatus(str, Enum):
    confirmed = "confirmed"
    pending = "pending"
    declined = "declined"
    canceled = "canceled"


class AccountType(str, Enum):
    user = "user"
    admin = "admin"


class Account(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    first_name: str
    last_name: str
    email: Optional[EmailStr] = Field(default=None)
    password: Optional[str] = Field(default=None, sa_column_kwargs={"nullable": True})
    description: Optional[str] = Field(default=None)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, nullable=False)
    trips: List["Trip"] = Relationship(back_populates="initiator")
    role: AccountType = Field(default=AccountType.user)


class AccountUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr] = None
    description: Optional[str]


class Trip(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    initiator_id: Optional[int] = Field(default=None, foreign_key="account.id")
    start_date: Optional[datetime.datetime] = None
    end_date: Optional[datetime.datetime] = None
    vehicle: Optional[VehicleType] = None
    description: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    status: TripStatus = Field(default=TripStatus.planned)

    initiator: Optional[Account] = Relationship(back_populates="trips")
    companions: List["Companion"] = Relationship(back_populates="trip")
    messages: List["Message"] = Relationship(back_populates="trip")
    itineraries: List["Itinerary"] = Relationship(back_populates="trip")


class Companion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int = Field(foreign_key="trip.id")
    companion_id: int = Field(foreign_key="account.id")
    status: CompanionStatus
    created_at: datetime.datetime

    trip: Trip = Relationship(back_populates="companions")
    companion: Account = Relationship()


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int = Field(foreign_key="trip.id")
    sender_id: int = Field(foreign_key="account.id")
    message: str
    created_at: datetime.datetime

    trip: Trip = Relationship(back_populates="messages")
    sender: Account = Relationship()


class Itinerary(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int = Field(foreign_key="trip.id")
    stop_number: int
    location: str
    arrival_date: Optional[datetime.datetime] = None
    departure_date: Optional[datetime.datetime] = None
    created_at: datetime.datetime

    trip: Trip = Relationship(back_populates="itineraries")


class AccountPublic(BaseModel):
    id: Optional[int]
    username: str
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    description: Optional[str] = None
    role: AccountType

    class Config:
        from_attributes = True


class CompanionPublic(BaseModel):
    id: Optional[int]
    first_name: str
    last_name: str
    status: CompanionStatus
    created_at: datetime.datetime


class TripWithCompanions(BaseModel):
    id: Optional[int]
    initiator: Optional[AccountPublic]
    start_date: Optional[datetime.datetime] = None
    end_date: Optional[datetime.datetime] = None
    vehicle: Optional[VehicleType] = None
    description: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    status: TripStatus = TripStatus.planned
    companions: list[CompanionPublic] = []
