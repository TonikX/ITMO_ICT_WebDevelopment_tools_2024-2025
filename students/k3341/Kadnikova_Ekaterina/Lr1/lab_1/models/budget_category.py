from typing import Optional
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship

class BudgetCategory(SQLModel, table=True):
    __tablename__ = "budgetcategory"
    id: Optional[int] = Field(default=None, primary_key=True)
    budget_id: int = Field(foreign_key="budget.id")
    category_id: int = Field(foreign_key="category.id")
    limit_amount: Decimal

    budget: Optional["Budget"] = Relationship(back_populates="categories")
    category: Optional["Category"] = Relationship(back_populates="budget_categories")