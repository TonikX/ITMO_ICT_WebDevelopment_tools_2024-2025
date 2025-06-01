from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

from models.transaction import Transaction


class Budget(SQLModel, table=True):
    __tablename__ = "budget"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    month: date
    current_amount: Decimal = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="budgets")
    categories: List["BudgetCategory"] = Relationship(back_populates="budget")