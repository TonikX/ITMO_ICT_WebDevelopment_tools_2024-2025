from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    amount: float
    type: str  # "income" or "expense"
    date: datetime = Field(default_factory=datetime.utcnow)
    description: Optional[str] = None

    # Relationships
    category: Optional["Category"] = Relationship(back_populates="transactions")
    tags: List["TransactionTag"] = Relationship(back_populates="transaction")
