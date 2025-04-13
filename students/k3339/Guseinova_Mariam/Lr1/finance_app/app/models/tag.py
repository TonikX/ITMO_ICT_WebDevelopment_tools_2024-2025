from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Tag(Base):
    __tablename__ = "tag"

    tag_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    transactions = relationship("TransactionTag", back_populates="tag", cascade="all, delete")

class TransactionTag(Base):
    __tablename__ = "transaction_tag"

    transaction_id = Column(Integer, ForeignKey("transaction.transaction_id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tag.tag_id", ondelete="CASCADE"), primary_key=True)
    context = Column(String, nullable=True)

    transaction = relationship("Transaction", back_populates="tags")
    tag = relationship("Tag", back_populates="transactions")