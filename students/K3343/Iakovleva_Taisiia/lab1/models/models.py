from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from enum import Enum
from datetime import datetime
from pydantic import BaseModel
from pydantic import EmailStr

# ENUM

class CategoryType(str, Enum):
    food = "food"
    transport = "transport"
    salary = "salary"
    entertainment = "entertainment"
    health = "health"
    other = "other"


# USER 
class UserDefault(SQLModel):
    username: str
    email: EmailStr = Field(unique=True, index=True)
    is_active: bool = True
    hashed_password: str

class UserCreate(SQLModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(SQLModel):
    username: str
    password: str

class UserRead(SQLModel):
    id: int
    email: EmailStr
    is_active: bool


class UserBudgetLink(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    budget_id: int = Field(foreign_key="budget.id", primary_key=True)

class User(UserDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    accounts: List["Account"] = Relationship(back_populates="user")
    # budgets: List["Budget"] = Relationship(back_populates="user")
    shared_budgets: List["Budget"] = Relationship(back_populates="users", link_model=UserBudgetLink)
    status: Optional[str] = Field(default=None)


class ChangePassword(BaseModel):
    old_password: str
    new_password: str


# ACCOUNT 
class AccountBase(SQLModel):
    name: str
    balance: float
    is_goal: bool = False
    target_amount: Optional[float] = None


class Account(AccountBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="accounts")
    transactions: List["Transaction"] = Relationship(back_populates="account")

class AccountDefault(SQLModel):
    user_id: int
    name: str
    is_goal: bool = False
    balance: float = 0.0  
    target_amount: Optional[float] = None # цель (только если is_goal=True)

# TRANSACTION 
class TransactionBase(SQLModel):
    amount: float
    description: str
    date: datetime
    category: CategoryType


class Transaction(TransactionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.id")
    account: Optional["Account"] = Relationship(back_populates="transactions")


class TransactionDefault(SQLModel):
    account_id: int
    category: CategoryType
    amount: float
    description: Optional[str]
    date: datetime

class TransactionResponse(BaseModel):
    transaction: Transaction
    warning: Optional[str] = None


# BUDGET 
class BudgetBase(SQLModel):
    month: int
    year: int
    limit: float
    category: CategoryType
    
class Budget(BudgetBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # user_id: int = Field(foreign_key="user.id")
    # user: Optional[User] = Relationship(back_populates="budgets")
    users: List["User"] = Relationship(back_populates="shared_budgets", link_model=UserBudgetLink)

class BudgetDefault(SQLModel):
    # user_id: int
    category: CategoryType
    month: int
    year: int
    limit: float
    user_ids: List[int]

class BudgetStats(BaseModel):
    id: int
    # user_id: int
    users: List[int]
    category: CategoryType
    month: int
    year: int
    limit: float
    spent: float
    remaining: float

# TRANSFER 
class TransferBase(SQLModel):
    amount: float
    date: datetime


class Transfer(TransferBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    from_account_id: int = Field(foreign_key="account.id")
    to_account_id: int = Field(foreign_key="account.id")


class TransferDefault(SQLModel):
    from_account_id: int
    to_account_id: int
    amount: float
    date: datetime
