from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str  

    transactions: List["Transaction"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")
    accounts: List["Account"] = Relationship(back_populates="user")
    goals: List["Goal"] = Relationship(back_populates="user")
    category_preferences: List["UserCategoryPreference"] = Relationship(back_populates="user")


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    transactions: List["Transaction"] = Relationship(back_populates="category")
    budgets: List["Budget"] = Relationship(back_populates="category")
    user_preferences: List["UserCategoryPreference"] = Relationship(back_populates="category")


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    account_id: Optional[int] = Field(default=None, foreign_key="account.id")

    amount: float
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="transactions")
    category: Optional[Category] = Relationship(back_populates="transactions")
    account: Optional["Account"] = Relationship(back_populates="transactions")


class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    limit_amount: float

    user: Optional[User] = Relationship(back_populates="budgets")
    category: Optional[Category] = Relationship(back_populates="budgets")


class Account(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    balance: float = 0.0

    user: Optional[User] = Relationship(back_populates="accounts")
    transactions: List[Transaction] = Relationship(back_populates="account")


class Goal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str
    target_amount: float
    deadline: Optional[datetime] = None
    current_amount: float = 0.0

    user: Optional[User] = Relationship(back_populates="goals")
    
class UserCategoryPreference(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    category_id: int = Field(foreign_key="category.id", primary_key=True)
    notification_enabled: bool = Field(default=True)

    user: Optional[User] = Relationship(back_populates="category_preferences")
    category: Optional[Category] = Relationship(back_populates="user_preferences")
