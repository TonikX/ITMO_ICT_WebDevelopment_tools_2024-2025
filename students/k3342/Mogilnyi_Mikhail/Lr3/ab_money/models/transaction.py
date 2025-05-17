from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .transaction_category import TransactionCategory
    from .user import User

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    amount: float
    description: Optional[str] = None
    type: str

    categories: List["TransactionCategory"] = Relationship(back_populates="transaction")
    user: Optional["User"] = Relationship(back_populates="transactions")
