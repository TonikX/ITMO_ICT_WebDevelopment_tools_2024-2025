from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class AccountBase(SQLModel):
    name: str
    currency: str = "USD"
    balance: float = 0.0

class Account(AccountBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")

    owner: Optional["User"] = Relationship(back_populates="accounts")
    transactions: List["Transaction"] = Relationship(back_populates="account")