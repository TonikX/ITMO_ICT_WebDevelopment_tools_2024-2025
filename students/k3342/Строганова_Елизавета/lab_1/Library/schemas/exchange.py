from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from schemas.relations import ExchangeRequestWithRelations

class ExchangeRequestBase(BaseModel):
    sender_id: int
    receiver_id: int
    sender_book_id: int
    desired_book_id: int
    status: str
    message: Optional[str] = None

class ExchangeRequestCreate(BaseModel):
    sender_book_id: int
    desired_book_id: int
    message: Optional[str] = None

class ExchangeRequestRead(ExchangeRequestBase):
    request_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ExchangeRequestUpdate(BaseModel):
    status: Optional[str] = None
    message: Optional[str] = None

class ExchangeBase(BaseModel):
    request_id: int
    completion_status: str
    user1_rating: Optional[int] = None
    user2_rating: Optional[int] = None
    feedback: Optional[str] = None

class ExchangeCreate(BaseModel):
    request_id: int
    completion_status: str = "в процессе"

class ExchangeRead(ExchangeBase):
    exchange_id: int
    exchange_date: datetime

    class Config:
        orm_mode = True

class ExchangeUpdate(BaseModel):
    completion_status: Optional[str] = None
    user1_rating: Optional[int] = None
    user2_rating: Optional[int] = None
    feedback: Optional[str] = None

class ExchangeWithRelations(ExchangeRead):
    request: ExchangeRequestWithRelations

    class Config:
        orm_mode = True