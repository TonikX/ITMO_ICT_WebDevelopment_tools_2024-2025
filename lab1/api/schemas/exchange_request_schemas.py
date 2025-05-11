from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from api.models.models import StatusExchange


class ExchangeRequestResponse(BaseModel):
    sender_id: int
    receiver_id: int
    sender_book_id: int
    requested_book_id: int
    status: StatusExchange
    created_at: datetime


class ExchangeRequestUpdateStatus(BaseModel):
    status: StatusExchange


class ExchangeRequestCreate(BaseModel):
    sender_id: int
    receiver_id: int
    sender_book_id: int
    requested_book_id: int
    status: StatusExchange
