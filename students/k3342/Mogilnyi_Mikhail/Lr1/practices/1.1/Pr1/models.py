from typing import List, Optional
from pydantic import BaseModel
from enum import Enum


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class Category(BaseModel):
    id: int
    name: str
    budget_limit: Optional[float] = None


class Transaction(BaseModel):
    id: int
    type: TransactionType
    amount: float
    category: Category
    description: Optional[str] = None


class Budget(BaseModel):
    category_id: int
    limit: float
