from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from LR1.models import BookStatus


class BookItemBase(BaseModel):
    title: str
    author: str
    description: Optional[str] = None


class BookItemCreate(BookItemBase):
    pass


class BookItemRead(BookItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)  # Включение ORM mode


class BookItemUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None


class UserBookBase(BaseModel):
    status: BookStatus = BookStatus.AVAILABLE


class UserBookCreate(UserBookBase):
    book_item_id: int


class UserBookRead(UserBookBase):
    book_item: BookItemRead
    user_profile_id: int
    model_config = ConfigDict(from_attributes=True)  # Включение ORM mode
