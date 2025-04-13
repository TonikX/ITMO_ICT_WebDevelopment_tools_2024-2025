from pydantic import BaseModel
from typing import Optional

class BookBase(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    genre: str
    publication_year: int
    condition: str
    description: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookRead(BookBase):
    book_id: int

    class Config:
        orm_mode = True

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    genre: Optional[str] = None
    publication_year: Optional[int] = None
    condition: Optional[str] = None
    description: Optional[str] = None