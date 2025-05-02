from typing import Optional, List

from pydantic import BaseModel

class Author(BaseModel):
    id: int
    name: str
    surname: str
    birth_year: int

class Genre(BaseModel):
    id: int
    name: str

class Book(BaseModel):
    id: int
    title: str
    year: int
    publisher: str
    author: Optional[Author]
    genres: Optional[List[Genre]]
