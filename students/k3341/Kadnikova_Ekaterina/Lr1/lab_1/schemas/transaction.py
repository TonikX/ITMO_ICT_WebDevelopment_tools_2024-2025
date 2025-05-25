from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlmodel import SQLModel

from models.transaction import LinkedObjectType


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"

class TransactionBase(SQLModel):
    amount: Decimal
    type: TransactionType
    description: str | None = None
    date: datetime
    category_id: int

class TransactionCreate(TransactionBase):
    linked_object_id: Optional[int] = None
    linked_object_type: Optional[LinkedObjectType] = None

class TransactionRead(TransactionBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class TransactionUpdate(SQLModel):
    category_id: Optional[int] = None
    type: Optional[TransactionType] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    date: Optional[str] = None
    linked_object_id: Optional[int] = None
    linked_object_type: Optional[LinkedObjectType] = None