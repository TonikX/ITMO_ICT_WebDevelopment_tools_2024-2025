from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from app.models.budget_category import BudgetCategory

class BudgetBase(SQLModel):
    name: str
    description: Optional[str] = None

class Budget(BudgetBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")

    owner: Optional["User"] = Relationship(back_populates="budgets")

    categories: List["Category"] = Relationship(back_populates="budgets", link_model=BudgetCategory)
    category_links: List["BudgetCategory"] = Relationship(back_populates="budget")