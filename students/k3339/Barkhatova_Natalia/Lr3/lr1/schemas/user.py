from typing import List, Optional, TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from schemas.book import Book
    from schemas.review import Review
    from schemas.location import Location


class UserBase(BaseModel):
    email: str
    username: str
    preferences: Optional[str] = None

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserUpdate(UserBase):
    email: Optional[str] = None
    username: Optional[str] = None
    preferences: Optional[str] = None


class User(UserBase):
    id: int
    books_as_owner: List["Book"] = []
    books_as_previous_owner: List["Book"] = []
    reviews_written: List["Review"] = []
    reviews_received: List["Review"] = []
    location: Optional["Location"] = None

    class Config:
        orm_mode = True


class UserShort(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True
