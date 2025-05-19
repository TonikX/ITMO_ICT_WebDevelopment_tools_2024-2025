from sqlalchemy import Column, Integer, Float, String, ForeignKey, Date, Table
from sqlalchemy.orm import relationship
from app.db.base import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    description = Column(String)
    date = Column(Date)
    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))

    user = relationship("User", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")
