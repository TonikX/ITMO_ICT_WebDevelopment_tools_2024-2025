import bcrypt
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from enum import Enum

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    hashed_password: str
    currency: str

    transactions: List["Transaction"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")

    def set_password(self, password: str):
        """Хэшируем пароль и сохраняет в базе данных"""
        self.hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password: str) -> bool:
        """Проверяем, совпадает ли введённый пароль с хэшированным"""
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    transaction_type: TransactionType
    date: str
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    link:str

    user: Optional["User"] = Relationship(back_populates="transactions")
    category_ref: Optional["Category"] = Relationship(back_populates="transactions")

class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    month: int
    year: int
    amount: float

    user: Optional["User"] = Relationship(back_populates="budgets")

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    transactions: List["Transaction"] = Relationship(back_populates="category_ref")
