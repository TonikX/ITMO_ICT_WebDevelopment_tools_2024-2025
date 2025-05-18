from typing import Optional
from sqlmodel import SQLModel


class BookBase(SQLModel):
    title: str
    author: str
    description: Optional[str] = None


class BookRead(SQLModel):
    id: int
    title: str
    author: str
    description: Optional[str] = None
