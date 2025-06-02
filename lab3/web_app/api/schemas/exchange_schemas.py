from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ExchangeResponse(BaseModel):
    id: Optional[int]
    sender_id: int
    receiver_id: int
    book_id: int
    confirmed_at: datetime


class ExchangeCreate(BaseModel):
    pass