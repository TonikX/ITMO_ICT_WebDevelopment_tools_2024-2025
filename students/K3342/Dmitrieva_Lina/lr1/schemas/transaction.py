from pydantic import BaseModel
from typing import Optional, List

from schemas.shared import TransactionType

class TransactionCreate(BaseModel):
    amount: float
    transaction_type: TransactionType
    date: str
    user_id: int
    category_id: Optional[int] = None

class TransactionRead(TransactionCreate):
    id: int

    class Config:
        from_attributes = True


