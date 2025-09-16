from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
import datetime
from enum import Enum

class CategoryType(str, Enum):
    income = "income"
    expense = "expense"

class NotificationType(str, Enum):
    over_budget = "over_budget"
    goal_achieved = "goal_achieved"
    goal_progress = "goal_progress"
    info = "info"

class NotificationStatus(str, Enum):
    unread = "unread"
    read = "read"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    status: str = Field(default="active")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    
    transactions: List["Transaction"] = Relationship(back_populates="user")
    categories: List["Category"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")
    goals: List["Goal"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    type: CategoryType
    status: str = Field(default="active")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    
    user: User = Relationship(back_populates="categories")
    transactions: List["Transaction"] = Relationship(back_populates="category")
    budgets: List["Budget"] = Relationship(back_populates="category")

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    amount: float
    date: datetime.date
    description: Optional[str] = None
    status: str = Field(default="completed")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    
    user: User = Relationship(back_populates="transactions")
    category: Category = Relationship(back_populates="transactions")

class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    limit_amount: float
    start_date: datetime.date
    end_date: datetime.date
    status: str = Field(default="active")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    
    user: User = Relationship(back_populates="budgets")
    category: Category = Relationship(back_populates="budgets")
    notifications: List["Notification"] = Relationship(back_populates="budget")

class Goal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str
    target_amount: float
    current_amount: float = Field(default=0)
    deadline: datetime.date
    status: str = Field(default="active")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    
    user: User = Relationship(back_populates="goals")
    notifications: List["Notification"] = Relationship(back_populates="goal")

class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    budget_id: Optional[int] = Field(default=None, foreign_key="budget.id")
    goal_id: Optional[int] = Field(default=None, foreign_key="goal.id")
    type: NotificationType
    title: str
    message: str
    status: NotificationStatus = Field(default=NotificationStatus.unread)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    
    user: User = Relationship(back_populates="notifications")
    budget: Optional[Budget] = Relationship(back_populates="notifications")
    goal: Optional[Goal] = Relationship(back_populates="notifications")