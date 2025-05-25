from enum import Enum

from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from models.base import Base


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"

class LinkedObjectType(str, Enum):
    goal = "goal"
    budget = "budget"

class TransactionModel(Base):
    __tablename__ = 'transaction'

    id = Column(Integer, primary_key=True)
    amount = Column(Float)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category", back_populates="transactions")