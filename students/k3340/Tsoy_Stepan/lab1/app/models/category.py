from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from app.models.budget_category import BudgetCategory

class CategoryBase(SQLModel):
    name: str
    is_income: bool = False

class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    transactions: List["Transaction"] = Relationship(back_populates="category")
    budgets: List["Budget"] = Relationship(back_populates="categories", link_model=BudgetCategory)

    budget_links: List["BudgetCategory"] = Relationship(back_populates="category")
