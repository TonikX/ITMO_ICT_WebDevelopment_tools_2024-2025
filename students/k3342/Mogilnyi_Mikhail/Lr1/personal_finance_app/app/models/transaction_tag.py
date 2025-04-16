from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class TransactionTag(SQLModel, table=True):
    transaction_id: int = Field(foreign_key="transaction.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)
    significance: int  # Extra field to characterize the relationship

    transaction: Optional["Transaction"] = Relationship(back_populates="tags")
    tag: Optional["Tag"] = Relationship(back_populates="transactions")
