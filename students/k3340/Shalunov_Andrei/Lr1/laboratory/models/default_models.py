from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field

class ProfileDefault(SQLModel):
    name: str
    email: str = Field(unique=True)
    password: str
    description: str
    register_date: date
    birth_date: date

class BookDefault(SQLModel):
    owner_id: int = Field(foreign_key="profile.id")
    info_id: int = Field(foreign_key="bookinfo.id")
    own_since: date

class BookInfoDefault(SQLModel):
    title: str
    author: str
    release_date: date
    genre: str
