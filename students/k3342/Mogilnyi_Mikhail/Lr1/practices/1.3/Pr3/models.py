from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import date


class BudgetCategoryLink(SQLModel, table=True):
    budget_id: Optional[int] = Field(default=None, foreign_key="budget.id", primary_key=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id", primary_key=True)


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    transactions: List["Transaction"] = Relationship(back_populates="category")
    budgets: List["Budget"] = Relationship(back_populates="categories", link_model=BudgetCategoryLink)


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    type: str
    date: date
    description: Optional[str] = None
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")

    category: Optional[Category] = Relationship(back_populates="transactions")
    note: Optional[str] = None


class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    month: str
    total_amount: float

    categories: List[Category] = Relationship(back_populates="budgets", link_model=BudgetCategoryLink)
