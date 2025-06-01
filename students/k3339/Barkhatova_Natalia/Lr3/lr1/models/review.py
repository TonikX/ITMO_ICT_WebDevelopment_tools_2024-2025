from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class Review(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    reviewed_user_id: int = Field(foreign_key="user.id")
    rating: int = Field(ge=1, le=6)
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    author: "User" = Relationship(back_populates="reviews_written",
                                  sa_relationship_kwargs={"foreign_keys": "[Review.user_id]"})
    target: "User" = Relationship(back_populates="reviews_received",
                                  sa_relationship_kwargs={"foreign_keys": "[Review.reviewed_user_id]"})
