from sqlmodel import SQLModel
from typing import Optional
from datetime import date


class UserRead(SQLModel):
    id: int
    username: str
    email: str


class CategoryRead(SQLModel):
    id: int
    name: str
    type: str


class BudgetBase(SQLModel):
    amount: float
    start_date: date
    end_date: date


class BudgetCreate(BudgetBase):
    user_id: int
    category_id: int


class BudgetRead(BudgetBase):
    id: int
    user: Optional[UserRead]
    category: Optional[CategoryRead]


class BudgetUpdate(SQLModel):
    amount: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
