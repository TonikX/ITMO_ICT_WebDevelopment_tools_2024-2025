from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import enum

class ExchangeStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    completed = "completed"

class ExchangeRequestBase(BaseModel):
    receiver_id: int
    sender_book_id: Optional[int] = None
    receiver_book_id: Optional[int] = None

class ExchangeRequestCreate(ExchangeRequestBase):
    pass

class ExchangeRequestRead(ExchangeRequestBase):
    id: int
    sender_id: int
    status: ExchangeStatus
    created_at: datetime

    class Config:
        from_attributes = True

class ExchangeStatusHistoryRead(BaseModel):
    id: int
    exchange_request_id: int
    status: ExchangeStatus
    changed_at: datetime

    class Config:
        from_attributes = True 