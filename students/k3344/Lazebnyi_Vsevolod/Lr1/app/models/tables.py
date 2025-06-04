from sqlmodel import SQLModel, Field, Relationship, Column, Enum
from typing import Optional, List
import enum
import datetime

class CategoryType(str, enum.Enum):
    income = "income"
    expense = "expense"

class NotificationType(str, enum.Enum):
    over_budget = "over_budget"
    goal_achieved = "goal_achieved"
    info = "info"

class NotificationStatus(str, enum.Enum):
    unread = "unread"
    read = "read"

class TransactionCategoryLink(SQLModel, table=True):
    transaction_id: Optional[int] = Field(
        default=None, foreign_key="transaction.id", primary_key=True
    )
    category_id: Optional[int] = Field(
        default=None, foreign_key="category.id", primary_key=True
    )

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    password_hash: str
    status: str = Field(default="active")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    transactions: List["Transaction"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")
    goals: List["Goal"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, nullable=False)
    type: str = Field(default=None)
    status: str = Field(default="active")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    transactions: List["Transaction"] = Relationship(back_populates="categories", link_model=TransactionCategoryLink)
    budgets: List["Budget"] = Relationship(back_populates="category")

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    amount: float = Field(nullable=False)
    date: datetime.date = Field(nullable=False)
    description: Optional[str] = None
    status: str = Field(default="completed")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    user: Optional[User] = Relationship(back_populates="transactions")
    categories: List[Category] = Relationship(back_populates="transactions", link_model=TransactionCategoryLink)

class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    category_id: int = Field(foreign_key="category.id", nullable=False)
    limit_amount: float = Field(nullable=False)
    start_date: datetime.date = Field(nullable=False)
    end_date: datetime.date = Field(nullable=False)
    status: str = Field(default="active")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    user: Optional[User] = Relationship(back_populates="budgets")
    category: Optional[Category] = Relationship(back_populates="budgets")
    notifications: List["Notification"] = Relationship(back_populates="budget")

class Goal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    title: str = Field(nullable=False)
    target_amount: float = Field(nullable=False)
    current_amount: float = Field(default=0, nullable=False)
    deadline: datetime.date = Field(nullable=False)
    status: str = Field(default="active")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    user: Optional[User] = Relationship(back_populates="goals")

class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    budget_id: int = Field(foreign_key="budget.id", nullable=False)
    type: NotificationType = Field(nullable=False)
    status: NotificationStatus = Field(default=NotificationStatus.unread)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    user: Optional[User] = Relationship(back_populates="notifications")
    budget: Optional[Budget] = Relationship(back_populates="notifications")