from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from models.base import Base


class TransactionCategory(Base):
    __tablename__ = "transaction_categories"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    weight = Column(Float, nullable=False)
    transaction = relationship("Transaction", back_populates="categories")
    category = relationship("Category", back_populates="transactions")
