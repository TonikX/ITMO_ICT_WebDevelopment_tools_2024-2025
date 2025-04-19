from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from typing import Optional, List

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

# Модели для запросов (без table=True)
class UserCreate(SQLModel):
    name: str
    email: str = Field(unique=True)
    currency: str = Field(default="USD", max_length=3)

class TransactionCreate(SQLModel):
    amount: float
    transaction_type: TransactionType
    date: str
    user_id: int

#Класс пользователя
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    transactions: List["Transaction"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "cascade": "all, delete",
        }
    )

#Класс транзакций
class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    user: Optional[User] = Relationship(back_populates="transactions")

    category: Optional[str] = Field(default=None)

# Для вложенного отображения User внутри Transaction
class TransactionWithUser(TransactionCreate):
    id: int
    user: Optional[UserCreate] = None

    class Config:
        from_attributes = True

# Для вложенного отображения Transaction внутри User
class UserWithTransactions(UserCreate):
    id: int
    transactions: List[TransactionCreate] = []

    class Config:
        from_attributes = True

