from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

class User(SQLModel, table=True):
    __tablename__ = "user"
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, nullable=False)
    email: str = Field(unique=True, nullable=False)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    transactions: List["Transaction"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")
    goals: List["Goal"] = Relationship(back_populates="user")