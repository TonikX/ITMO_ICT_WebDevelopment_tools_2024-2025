from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from models.transaction import TransactionType


class TransactionBase(BaseModel):
    amount: float
    date: datetime
    description: str | None = None
    type: TransactionType


class TransactionCreate(TransactionBase):
    category_id: int
    weight: float


class TransactionResponse(TransactionBase):
    id: int
    categories: list[str]
    user_id: int

    class Config:
        from_attributes = True


class ExpenseSummaryResponse(BaseModel):
    category: str
    total_spent: float