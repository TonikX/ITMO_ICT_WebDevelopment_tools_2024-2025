from sqlmodel import SQLModel, Field
from .book import BookRead
from .profile import ProfileRead


class ExchangeRequestBase(SQLModel):
    status: str = Field(default="pending")
    requester_id: int = Field(foreign_key="profile.id")
    requested_book_id: int = Field(foreign_key="book.id")


class ExchangeRequestRead(SQLModel):
    id: int
    status: str
    requester: ProfileRead
    book: BookRead
