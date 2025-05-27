from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class TransactionBase(SQLModel):
    amount: float
    description: Optional[str] = None
    type : str


class UserRead(SQLModel):
    id: int
    username: str
    email: str


class TransactionCreate(TransactionBase):
    user_id: int


class TransactionRead(TransactionBase):
    id: int
    date: datetime
    user: Optional[UserRead]


class TransactionUpdate(SQLModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    type: Optional[str] = None
