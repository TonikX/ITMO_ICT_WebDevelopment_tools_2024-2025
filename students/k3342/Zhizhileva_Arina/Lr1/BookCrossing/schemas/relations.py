from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from schemas.user import UserRead
from schemas.book import BookRead
from schemas.user_book import UserBookRead

class UserBookWithRelations(UserBookRead):
    user: UserRead
    book: BookRead

    class Config:
        orm_mode = True

class ExchangeRequestWithRelations(BaseModel):
    request_id: int
    sender: UserRead
    receiver: UserRead
    sender_book: UserBookWithRelations
    desired_book: UserBookWithRelations
    status: str
    created_at: datetime
    updated_at: datetime
    message: Optional[str] = None

    class Config:
        orm_mode = True

class UserWithRelations(UserRead):
    books: List[UserBookWithRelations] = []
    sent_requests: List[ExchangeRequestWithRelations] = []
    received_requests: List[ExchangeRequestWithRelations] = []

    class Config:
        orm_mode = True

class BookWithRelations(BookRead):
    owners: List[UserBookWithRelations] = []

    class Config:
        orm_mode = True