from pydantic import BaseModel
from typing import Optional

class UserBookBase(BaseModel):
    book_id: int
    is_available: Optional[bool] = True

class UserBookCreate(UserBookBase):
    pass

class UserBookRead(UserBookBase):
    id: int
    user_id: int
    book_title: Optional[str] = None
    book_author: Optional[str] = None

    class Config:
        from_attributes = True

class UserBookUpdateAvailability(BaseModel):
    is_available: bool 