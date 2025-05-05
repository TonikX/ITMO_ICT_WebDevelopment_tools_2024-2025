from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import date


class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    period_start: date
    period_end: date
    user_id: int = Field(foreign_key="user.id")

    category_links: List["BudgetCategoryLink"] = Relationship(back_populates="budget")


class BudgetCategoryLink(SQLModel, table=True):
    budget_id: int = Field(foreign_key="budget.id", primary_key=True)
    category_id: int = Field(foreign_key="category.id", primary_key=True)
    planned_amount: float

    budget: Budget = Relationship(back_populates="category_links")
    category: "Category" = Relationship()


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    transaction_categories: List["TransactionCategory"] = Relationship(back_populates="category")


class Goal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str
    amount: float
    description: Optional[str] = None


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    amount: float
    description: Optional[str] = None
    type: str

    user: "User" = Relationship(back_populates="transactions")
    categories: List["TransactionCategory"] = Relationship(back_populates="transaction")


class TransactionCategory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: int = Field(foreign_key="transaction.id")
    category_id: int = Field(foreign_key="category.id")
    amount: float

    transaction: "Transaction" = Relationship(back_populates="categories")
    category: "Category" = Relationship(back_populates="transaction_categories")


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str

    transactions: List["Transaction"] = Relationship(back_populates="user")
