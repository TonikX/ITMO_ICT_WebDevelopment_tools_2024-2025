from typing import List, Optional
from enum import Enum
from pydantic import BaseModel

from schemas import CategoryRead


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"

class TransactionBase(BaseModel):
    amount: float
    description: Optional[str] = None
    type: TransactionType

class TransactionCreate(TransactionBase):
    category_ids: List[int] = []

class TransactionRead(TransactionBase):
    id: int
    user_id: int
    categories: List[CategoryRead]

    class Config:
        from_attributes = True

