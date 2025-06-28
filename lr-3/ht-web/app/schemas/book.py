from pydantic import BaseModel
from typing import Optional

class BookBase(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
    isbn: Optional[str] = None
    genre: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookRead(BookBase):
    id: int
    owner_id: int
    owner_email: Optional[str] = None

    class Config:
        from_attributes = True 