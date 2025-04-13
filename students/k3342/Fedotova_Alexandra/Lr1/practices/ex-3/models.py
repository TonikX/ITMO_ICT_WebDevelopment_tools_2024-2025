from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    age: Optional[int] = Field(default=None)
    bio: Optional[str] = Field(default=None)

    trips: List["Trip"] = Relationship(back_populates="owner")
    trip_requests: List["TripRequest"] = Relationship(back_populates="user")

class TripPreference(SQLModel, table=True):
    trip_id: int = Field(foreign_key="trip.id", primary_key=True)
    preference_id: int = Field(foreign_key="preference.id", primary_key=True)

class Trip(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id", index=True)
    destination: str
    start_date: datetime
    end_date: datetime
    description: Optional[str] = Field(default=None)

    owner: User = Relationship(back_populates="trips")
    trip_requests: List["TripRequest"] = Relationship(back_populates="trip")
    preferences: List["Preference"] = Relationship(
        back_populates="trips",
        link_model=TripPreference
    )
    messages: List["Message"] = Relationship(back_populates="trip")

class Preference(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    trips: List["Trip"] = Relationship(
        back_populates="preferences",
        link_model=TripPreference
    )

class TripRequest(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    trip_id: int = Field(foreign_key="trip.id", index=True)
    status: str = Field(default="pending")  # pending, accepted, rejected

    user: User = Relationship(back_populates="trip_requests")
    trip: Trip = Relationship(back_populates="trip_requests")

class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="user.id", index=True)
    trip_id: int = Field(foreign_key="trip.id", index=True)
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    sender: User = Relationship()
    trip: Trip = Relationship(back_populates="messages")


class FavoriteTrip(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    trip_id: int = Field(foreign_key="trip.id", primary_key=True)

