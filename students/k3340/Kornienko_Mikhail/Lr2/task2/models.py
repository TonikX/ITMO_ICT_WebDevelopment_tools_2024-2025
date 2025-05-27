from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    email: Optional[str] = None
    contact_number: Optional[str] = None
    is_confirmed: bool = Field(default=False)
    is_organizer: bool = Field(default=False)


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: Optional[str]
    description: Optional[str]
    requirements: Optional[str]
    evaluation_criteria: Optional[str]
    user_id: Optional[int] = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
