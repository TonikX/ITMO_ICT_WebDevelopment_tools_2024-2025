from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import date, datetime
from pydantic import BaseModel, EmailStr



class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


# --- Ассоциативная таблица между Goal и Category с дополнительным полем ---
class GoalCategoryLink(SQLModel, table=True):
    goal_id: Optional[int] = Field(default=None, foreign_key="goal.id", primary_key=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id", primary_key=True)
    allocated_amount: float = 0.0


# --- Пользователь ---
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    transactions: List["Transaction"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")
    goals: List["Goal"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")
    categories: List["Category"] = Relationship(back_populates="user")

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

# модель для смены пароля
class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str


# --- Категории доходов и расходов ---
class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    is_income: bool = False
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    user: Optional[User] = Relationship(back_populates="categories")
    transactions: List["Transaction"] = Relationship(back_populates="category")
    budgets: List["Budget"] = Relationship(back_populates="category")
    goals: List["Goal"] = Relationship(back_populates="categories", link_model=GoalCategoryLink)


# --- Транзакции ---
class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    amount: float
    type: TransactionType
    date: date
    description: Optional[str] = ""

    user: User = Relationship(back_populates="transactions")
    category: Category = Relationship(back_populates="transactions")


# --- Бюджет по категориям ---
class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    amount: float
    start_date: date
    end_date: date

    user: User = Relationship(back_populates="budgets")
    category: Category = Relationship(back_populates="budgets")


# --- Финансовая цель ---
class Goal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    target_amount: float
    current_amount: float = 0.0
    due_date: date

    user: User = Relationship(back_populates="goals")
    categories: List[Category] = Relationship(back_populates="goals", link_model=GoalCategoryLink)


# --- Уведомления ---
class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    message: str
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship(back_populates="notifications")