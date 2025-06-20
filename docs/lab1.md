# Добро пожаловать в документацию проекта!

## О проекте
## Разработка веб-приложения для поиска партнеров в путешествие.

### models.py

```python
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


class UserRead(UserBase):
    id: int
    trips: List[TripRead]
    trip_requests: List[TripRequestRead]
    saved_trips: List[TripRead]


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
```

### trips.py

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from db import get_session
from models import *

router = APIRouter()


@router.post("/create", response_model=TripRead)
def create_trip(trip: TripCreate, session: Session = Depends(get_session)):
    db_trip = Trip.from_orm(trip)
    session.add(db_trip)
    session.commit()
    session.refresh(db_trip)
    return db_trip


@router.get("/search", response_model=List[TripRead])
def search_rides(
        destination: Optional[str] = Query(None),
        date: Optional[date] = Query(None),
        db: Session = Depends(get_session)
):
    query = select(Trip)
    if destination:
        query = query.where(Trip.destination == destination)
    if date:
        query = query.where(Trip.start_date <= date, Trip.end_date >= date)
    results = db.exec(query).all()
    return results


@router.get("/{trip_id}", response_model=TripWithDetails)
def get_trip(trip_id: int, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@router.get("/", response_model=List[TripRead])
def list_trips(session: Session = Depends(get_session)):
    return session.query(Trip).all()


@router.patch("/{trip_id}", response_model=TripRead)
def update_trip(trip_id: int, trip: TripUpdate, session: Session = Depends(get_session)):
    db_trip = session.get(Trip, trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    trip_data = trip.model_dump(exclude_unset=True)
    for key, value in trip_data.items():
        setattr(db_trip, key, value)
    session.commit()
    session.refresh(db_trip)
    return db_trip


@router.delete("/delete/{trip_id}")
def delete_trip(trip_id: int, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    for request in trip.trip_requests:
        session.delete(request)

    for saved_trip in trip.saved_by_users:
        session.delete(saved_trip)
    session.delete(trip)
    session.commit()

    return {"status": 200, "message": "Trip deleted"}


@router.get("/{trip_id}/trip_requests", response_model=List[TripRequestWithDetails])
def get_trip_requests(trip_id: int, session: Session = Depends(get_session)):
    trip_requests = session.exec(
        select(TripRequest)
        .options(selectinload(TripRequest.trip), selectinload(TripRequest.user))
        .where(TripRequest.trip_id == trip_id)
    ).all()
    if not trip_requests:
        raise HTTPException(status_code=404, detail="No trip requests found")
    return trip_requests


@router.put("/update/{trip_id}", response_model=TripRead)
def update_trip(trip_id: int, trip: TripUpdate, session: Session = Depends(get_session)):
    db_trip = session.get(Trip, trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    for key, value in trip.dict(exclude_unset=True).items():
        setattr(db_trip, key, value)

    session.commit()
    session.refresh(db_trip)

    return db_trip


@router.get("/trips_vlozhenn/{trip_id}", response_model=TripWithDetails)
def get_trip(trip_id: int, session: Session = Depends(get_session)):
    trip = session.exec(
        select(Trip)
        .options(selectinload(Trip.user), selectinload(Trip.organizer))
        .where(Trip.id == trip_id)
    ).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip
```
