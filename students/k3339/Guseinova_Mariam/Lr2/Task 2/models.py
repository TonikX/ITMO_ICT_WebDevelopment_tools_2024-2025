from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    name: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None, unique=True)
    hashed_password: str
    registration_date: datetime = Field(default=datetime.now())