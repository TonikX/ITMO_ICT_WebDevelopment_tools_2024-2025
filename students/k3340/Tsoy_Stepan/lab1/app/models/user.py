from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class UserBase(SQLModel):
    email: str
    full_name: Optional[str] = None

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

    accounts: List["Account"] = Relationship(back_populates="owner")
    budgets: List["Budget"] = Relationship(back_populates="owner")
    transactions: List["Transaction"] = Relationship(back_populates="user")