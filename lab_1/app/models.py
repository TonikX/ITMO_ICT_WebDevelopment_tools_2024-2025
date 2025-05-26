from datetime import date
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"

# Модель категории – отношение один ко многим (одна категория → много транзакций)
class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    budget: float  # лимит для расходов в этой категории
    # Обратное отношение: список транзакций, принадлежащих данной категории
    transactions: List["Transaction"] = Relationship(back_populates="category")

# Ассоциативная таблица для связи «многие‑ко‑многим» между транзакциями и тегами
class TransactionTagLink(SQLModel, table=True):
    transaction_id: Optional[int] = Field(default=None, foreign_key="transaction.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)
    note: Optional[str] = Field(default=None, description="Комментарий или пометка к связи тега с транзакцией")

# Модель тега – отношение многие ко многим (один тег ↔ много транзакций)
class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    # Обратное отношение к транзакциям
    transactions: List["Transaction"] = Relationship(back_populates="tags", link_model=TransactionTagLink)

# Модель транзакции – содержит ссылку на категорию (one-to-many) и набор тегов (many-to-many)
class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: TransactionType  # income или expense
    amount: float
    date: date
    description: Optional[str] = None
    # Внешний ключ для категории
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    # Отношение к категории – для возврата вложенных данных
    category: Optional[Category] = Relationship(back_populates="transactions")
    # Отношение многие ко многим с тегами
    tags: List[Tag] = Relationship(back_populates="transactions", link_model=TransactionTagLink)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str


class UserCreate(SQLModel):
    username: str
    password: str

# Для ответа (без пароля)
class UserRead(SQLModel):
    id: int
    username: str