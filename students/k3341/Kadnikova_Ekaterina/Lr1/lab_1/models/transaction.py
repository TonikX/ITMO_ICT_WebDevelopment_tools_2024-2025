from datetime import datetime
from typing import Optional
from decimal import Decimal
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship

class TransactionType(str, Enum):
    income = "income"
    expense = "expense"

class LinkedObjectType(str, Enum):
    goal = "goal"
    budget = "budget"

class Transaction(SQLModel, table=True):
    __tablename__ = "transaction"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    amount: Decimal
    type: TransactionType
    description: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)

    linked_object_id: Optional[int] = Field(default=None)
    linked_object_type: Optional[LinkedObjectType] = Field(default=None)

    user: Optional["User"] = Relationship(back_populates="transactions")
    category: Optional["Category"] = Relationship(back_populates="transactions")