from typing import List

from pydantic import BaseModel
from enum import Enum
from pydantic import Field
from app.schemas.transaction import TransactionOut

class CategoryType(str, Enum):
    income = "income"
    expense = "expense"

class CategoryBase(BaseModel):
    name: str
    type: CategoryType

class CategoryCreate(CategoryBase):
    type: CategoryType = Field(..., example="income")  # Явно указываем пример

class CategoryOut(CategoryBase):
    category_id: int

    class Config:
        from_attributes = True

class CategoryOutWithTransactions(CategoryBase):
    category_id: int
    transactions: List[TransactionOut] = []  # Добавляем список транзакций

    class Config:
        from_attributes = True

class CategoryUpdate(BaseModel):
    name: str | None = None
    type: CategoryType | None = None