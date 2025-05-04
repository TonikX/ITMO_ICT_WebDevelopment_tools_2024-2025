from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import date


class UserBase(SQLModel):
    name: str
    email: str
    preferences: Optional[str] = None


class User(UserBase, table=True):
    __tablename__ = "user"
    id: int = Field(default=None, primary_key=True)

    trips: List["Trip"] = Relationship(back_populates="user")
    trip_requests: List["TripRequest"] = Relationship(back_populates="user")
    saved_trips: List["SavedTrip"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int


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
    start_date: date
    end_date: date
    description: Optional[str] = None


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


# Вложенность
class TripWithDetails(TripRead):
    user: Optional[UserRead]
    organizer: Optional[OrganizerRead]


class TripRequestBase(SQLModel):
    status: str


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


class SavedTrip(SQLModel, table=True):
    __tablename__ = "savedtrip"
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    trip_id: int = Field(foreign_key="trip.id", primary_key=True)

    saved_at: Optional[date] = Field(default_factory=date.today)

    user: "User" = Relationship(back_populates="saved_trips")
    trip: "Trip" = Relationship(back_populates="saved_by_users")
