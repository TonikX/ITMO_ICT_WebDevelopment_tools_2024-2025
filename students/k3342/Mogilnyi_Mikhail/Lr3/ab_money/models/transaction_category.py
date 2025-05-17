from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .transaction import Transaction
    from .category import Category

class TransactionCategory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: int = Field(foreign_key="transaction.id")
    category_id: int = Field(foreign_key="category.id")
    amount: float

    transaction: Optional["Transaction"] = Relationship(back_populates="categories")
    category: Optional["Category"] = Relationship()
