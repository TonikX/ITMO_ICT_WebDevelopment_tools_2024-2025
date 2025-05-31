from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from models.user_model import UserRead


class ReviewDefault(SQLModel):
    rating: int
    comment: Optional[str] = None


class Review(ReviewDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int = Field(foreign_key="trip.id")
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    trip: Optional["Trip"] = Relationship(back_populates="reviews")
    user: Optional["User"] = Relationship(back_populates="reviews")


class ReviewDetails(ReviewDefault):
    id: int
    created_at: datetime
    trip_id: int
    user: Optional[UserRead] = None