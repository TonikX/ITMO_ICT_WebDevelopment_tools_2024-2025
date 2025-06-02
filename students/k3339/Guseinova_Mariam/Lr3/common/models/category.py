from sqlalchemy import Column, Integer, String, Enum
from common.models.base import Base
from sqlalchemy.orm import relationship


class Category(Base):
    __tablename__ = "category"

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    type = Column(Enum("income", "expense", name="category_type"), nullable=False)
    transactions = relationship("Transaction", back_populates="category", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="category", cascade="all, delete")
