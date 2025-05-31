from typing import Optional, List
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

from models.trip_participant_model import TripParticipant
from models.message_model import Message
from models.review_model import Review
from models.user_model import UserRead



class Country(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


class TripDefault(SQLModel):
    title: str
    departure: str
    destination: str
    start_date: date
    end_date: date
    description: Optional[str] = None


class Trip(TripDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    creator_id: Optional[int] = Field(default=None, foreign_key="user.id")
    country_id: Optional[int] = Field(default=None, foreign_key="country.id")

    creator: Optional["User"] = Relationship(back_populates="trips_created")
    participants: Optional[List["User"]] = Relationship(back_populates="trips_joined", link_model=TripParticipant)
    reviews: Optional[List["Review"]] = Relationship(back_populates="trip")
    messages: Optional[List["Message"]] = Relationship(back_populates="trip")


class TripWithFullDetails(TripDefault):
    id: int
    creator: Optional[UserRead] = None
    participants: List[UserRead] = []
    reviews: List[Review] = []
    messages: List[Message] = []


class TripCreate(SQLModel):
    title: str
    departure: str
    destination: str
    start_date: date
    end_date: date
    description: Optional[str] = None


class TripUpdate(SQLModel):
    title: Optional[str] = None
    departure: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None


class TripParse(SQLModel):
    urls: List[str]