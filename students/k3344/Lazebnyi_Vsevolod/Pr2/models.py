from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from datetime import datetime

class CategoryType(str, Enum):
    income = "income"
    expense = "expense"

class NotificationType(str, Enum):
    over_budget = "over_budget"
    goal_achieved = "goal_achieved"
    info = "info"

class NotificationStatus(str, Enum):
    unread = "unread"
    read = "read"

class StatusType(str, Enum):
    active = "active"
    inactive = "inactive"

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(unique=True)
    password_hash: str
    status: StatusType = Field(default=StatusType.active)
    created_at: datetime = Field(default_factory=datetime.now)

class CategoryBase(SQLModel):
    name: str = Field(unique=True)
    type: CategoryType
    status: StatusType = Field(default=StatusType.active)
    created_at: datetime = Field(default_factory=datetime.now)

class TransactionBase(SQLModel):
    amount: float
    date: datetime = Field(default_factory=datetime.now)
    description: Optional[str] = ""
    status: StatusType = Field(default=StatusType.active)

class BudgetBase(SQLModel):
    limit_amount: float
    start_date: datetime
    end_date: datetime
    status: StatusType = Field(default=StatusType.active)
    created_at: datetime = Field(default_factory=datetime.now)

class GoalBase(SQLModel):
    title: str
    target_amount: float
    current_amount: float = Field(default=0)
    deadline: datetime
    status: StatusType = Field(default=StatusType.active)
    created_at: datetime = Field(default_factory=datetime.now)

class NotificationBase(SQLModel):
    type: NotificationType
    status: NotificationStatus = Field(default=NotificationStatus.unread)
    created_at: datetime = Field(default_factory=datetime.now)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transactions: List["Transaction"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")
    goals: List["Goal"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")

class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transactions: List["Transaction"] = Relationship(back_populates="category")
    budgets: List["Budget"] = Relationship(back_populates="category")

class Transaction(TransactionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="transactions")
    category_id: int = Field(foreign_key="category.id")
    category: Category = Relationship(back_populates="transactions")

class Budget(BudgetBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="budgets")
    category_id: int = Field(foreign_key="category.id")
    category: Category = Relationship(back_populates="budgets")

class Goal(GoalBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="goals")

class Notification(NotificationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="notifications")
    budget_id: int = Field(foreign_key="budget.id")
    budget: Budget = Relationship()