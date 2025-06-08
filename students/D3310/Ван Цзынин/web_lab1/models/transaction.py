from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from .user import User

class Transaction(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    amount: float
    category: str
    description: Optional[str] = ""
    transaction_type: str = Field(default="expense", description="income/expense")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="incomes" if transaction_type == "income" else "expenses")

    # 外键：关联分类（可选）
    category_id: Optional[int] = Field(foreign_key="category.id", default=None)
    category: Optional["Category"] = Relationship(back_populates="transactions")
    budget_links: List["BudgetExpenseLink"] = Relationship(back_populates="expense")