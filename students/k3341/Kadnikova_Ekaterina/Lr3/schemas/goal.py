from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

from sqlmodel import SQLModel


class GoalBase(SQLModel):
    title: str
    target_amount: Decimal
    current_amount: Decimal = 0
    due_date: date

class GoalCreate(GoalBase):
    pass

class GoalUpdate(SQLModel):
    name: Optional[str] = None
    target_amount: Optional[float] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True

class TransactionRead(SQLModel):
    id: int
    category_id: int
    type: str
    description: str
    amount: float
    date: datetime

    class Config:
        orm_mode = True

class GoalRead(GoalBase):
    id: int
    user_id: int
    created_at: datetime
    due_date: datetime
    transactions: List[TransactionRead]

    class Config:
        orm_mode = True