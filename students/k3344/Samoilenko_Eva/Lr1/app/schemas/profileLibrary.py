from .profile import ProfileRead
from .book import BookRead
from typing import List
from sqlmodel import SQLModel, Field


class ProfileLibraryBase(SQLModel):
    profile_id: int = Field(foreign_key="profile.id")


class ProfileLibraryRead(SQLModel):
    id: int
    owner: ProfileRead
    books: List[BookRead] = []
