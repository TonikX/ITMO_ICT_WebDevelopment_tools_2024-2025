from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, date


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=50)
    email: str = Field(unique=True, index=True, max_length=100)
    password_hash: str
    balance: float = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    transactions: List["Transaction"] = Relationship(back_populates="user")
    categories: List["Category"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")
    goals: List["Goal"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")


class UserDefault(SQLModel):
    username: str
    email: str
    password_hash: str


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str = Field(max_length=100)
    type: str

    user: Optional[User] = Relationship(back_populates="categories")
    budgets: List["Budget"] = Relationship(back_populates="category")


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    amount: float
    date: datetime = Field(default_factory=datetime.utcnow)
    description: Optional[str] = None
    type: str

    user: Optional[User] = Relationship(back_populates="transactions")


class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    amount: float
    start_date: date
    end_date: date

    user: Optional[User] = Relationship(back_populates="budgets")
    category: Optional[Category] = Relationship(back_populates="budgets")


class Goal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str = Field(max_length=100)
    target_amount: float
    current_amount: float = Field(default=0)
    due_date: Optional[date] = None

    user: Optional[User] = Relationship(back_populates="goals")


class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    message: str
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="notifications")


class GoalDefault(SQLModel):
    user_id: int
    name: str = Field(max_length=100)
    target_amount: float
    current_amount: float = Field(default=0)
    due_date: Optional[date] = None


class NotificationDefault(SQLModel):
    user_id: int
    message: str
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
