from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from models.user_model import UserRead

if TYPE_CHECKING:
    from models.trip_model import Trip
    from models.user_model import User


class MessageDefault(SQLModel):
    content: str


class Message(MessageDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int = Field(foreign_key="trip.id")
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    trip: Optional["Trip"] = Relationship(back_populates="messages")
    user: Optional["User"] = Relationship(back_populates="messages")


class MessageDetails(MessageDefault):
    id: int
    created_at: datetime
    trip_id: int
    user: Optional[UserRead] = None
