from sqlalchemy import Column, Integer, Float, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.db.base import Base


class Income(Base):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    source = Column(String)
    date = Column(Date)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="incomes")
