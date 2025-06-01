from datetime import date, datetime
from typing import List
from sqlmodel import SQLModel, Field
from schemas.category import CategoryRead


class BudgetBase(SQLModel):
    month: date

class BudgetCreate(BudgetBase):
    categories: List[int] = []

    class Config:
        orm_mode = True

class BudgetCategoryRead(SQLModel):
    category_id: int
    limit_amount: float
    category: CategoryRead
    current_amount: float

    class Config:
        orm_mode = True

class TransactionRead(SQLModel):
    id: int
    amount: float
    description: str
    date: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

class BudgetRead(BudgetBase):
    id: int
    user_id: int
    created_at: datetime
    categories: List[BudgetCategoryRead]
    transactions: List[TransactionRead]

    class Config:
        orm_mode = True

class BudgetCategoryUpdate(SQLModel):
    category_id: int
    limit_amount: float

class BudgetUpdate(SQLModel):
    month: date
    categories: List[BudgetCategoryUpdate]

    class Config:
        orm_mode = True