from typing import Optional
from sqlmodel import SQLModel


class ProfileBase(SQLModel):
    username: str
    bio: Optional[str] = None
    experience: Optional[str] = None
    preferences: Optional[str] = None


class ProfileRead(SQLModel):
    id: int
    username: str
    