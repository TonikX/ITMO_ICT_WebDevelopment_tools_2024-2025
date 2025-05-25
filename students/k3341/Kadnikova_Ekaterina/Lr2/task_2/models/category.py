from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from models.base import Base


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    is_income = Column(Boolean)
    # transactions = relationship("TransactionModel", back_populates="category")