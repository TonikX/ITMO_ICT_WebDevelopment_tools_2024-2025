from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TransactionBase(BaseModel):
    user_id: int
    category_id: int
    amount: float
    type: str
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionRead(TransactionBase):
    id: int
    date: datetime

    class Config:
        orm_mode = True

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
