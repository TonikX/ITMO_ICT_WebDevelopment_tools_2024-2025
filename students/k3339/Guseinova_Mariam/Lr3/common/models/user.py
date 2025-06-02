from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from common.models.base import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    registration_date = Column(DateTime, default=datetime.utcnow)
    transactions = relationship("Transaction", back_populates="user")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete")
    goals = relationship("Goal", back_populates="user", cascade="all, delete")
