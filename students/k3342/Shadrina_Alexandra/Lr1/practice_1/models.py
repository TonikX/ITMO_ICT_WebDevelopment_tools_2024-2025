from typing import List, Optional
from pydantic import BaseModel, EmailStr


class Profile(BaseModel):
    full_name: str
    email: EmailStr


class Book(BaseModel):
    id: int
    title: str
    author: str


class User(BaseModel):
    id: int
    username: str
    profile: Profile
    books: Optional[List[Book]] = []
