from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class TripParticipant(SQLModel, table=True):
    trip_id: Optional[int] = Field(default=None, foreign_key="trip.id", primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    status: str = Field(default="pending")
    joined_at: datetime = Field(default_factory=datetime.utcnow)
