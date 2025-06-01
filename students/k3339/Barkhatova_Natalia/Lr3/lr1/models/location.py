from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class Location(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    city: str
    region: Optional[str] = None

    user: "User" = Relationship(back_populates="location")
