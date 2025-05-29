from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBookBase(BaseModel):
    user_id: int
    book_id: int
    status: str
    location: Optional[str] = None

class UserBookCreate(UserBookBase):
    pass

class UserBookRead(UserBookBase):
    user_book_id: int
    added_at: datetime

    class Config:
        orm_mode = True

class UserBookUpdate(BaseModel):
    status: Optional[str] = None
    location: Optional[str] = None