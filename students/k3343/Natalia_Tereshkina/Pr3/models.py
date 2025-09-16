from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr

class CategoryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class NotificationType(str, Enum):
    OVER_BUDGET = "over_budget"
    GOAL_ACHIEVED = "goal_achieved"
    GOAL_PROGRESS = "goal_progress"
    INFO = "info"

class NotificationStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"

# Модели без отношений
class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    email: EmailStr = Field(unique=True, index=True)
    password_hash: str
    status: str = Field(default="active")

class CategoryBase(SQLModel):
    name: str
    type: CategoryType
    status: str = Field(default="active")

class TransactionBase(SQLModel):
    amount: float
    date: datetime
    description: Optional[str] = None
    status: str = Field(default="completed")

class BudgetBase(SQLModel):
    limit_amount: float
    start_date: datetime
    end_date: datetime
    status: str = Field(default="active")

class GoalBase(SQLModel):
    title: str
    target_amount: float
    current_amount: float = Field(default=0)
    deadline: datetime
    status: str = Field(default="active")

class NotificationBase(SQLModel):
    type: NotificationType
    title: str
    message: str
    status: NotificationStatus = Field(default=NotificationStatus.UNREAD)

# Модели с отношениями
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    categories: List["Category"] = Relationship(back_populates="user")
    transactions: List["Transaction"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")
    goals: List["Goal"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")

class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="categories")
    transactions: List["Transaction"] = Relationship(back_populates="category")
    budgets: List["Budget"] = Relationship(back_populates="category")

class Transaction(TransactionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="transactions")
    category: Category = Relationship(back_populates="transactions")

class Budget(BudgetBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="budgets")
    category: Category = Relationship(back_populates="budgets")
    notifications: List["Notification"] = Relationship(back_populates="budget")

class Goal(GoalBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="goals")
    notifications: List["Notification"] = Relationship(back_populates="goal")

class Notification(NotificationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    budget_id: Optional[int] = Field(default=None, foreign_key="budget.id")
    goal_id: Optional[int] = Field(default=None, foreign_key="goal.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="notifications")
    budget: Optional[Budget] = Relationship(back_populates="notifications")
    goal: Optional[Goal] = Relationship(back_populates="notifications")