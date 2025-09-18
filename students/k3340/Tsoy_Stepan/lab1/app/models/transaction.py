from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class TransactionBase(SQLModel):
    amount: float
    description: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_income: bool = False

class Transaction(TransactionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.id")
    category_id: int = Field(foreign_key="category.id")
    user_id: int = Field(foreign_key="user.id")

    account: Optional["Account"] = Relationship(back_populates="transactions")
    category: Optional["Category"] = Relationship(back_populates="transactions")
    user: Optional["User"] = Relationship(back_populates="transactions")