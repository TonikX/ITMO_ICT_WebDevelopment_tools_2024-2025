from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    full_name = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)  # Можно заменить на отдельную таблицу Skill
    experience = Column(Text, nullable=True)
    preferences = Column(Text, nullable=True)

    books = relationship("UserBook", back_populates="user")
    sent_requests = relationship("ExchangeRequest", back_populates="sender", foreign_keys='ExchangeRequest.sender_id')
    received_requests = relationship("ExchangeRequest", back_populates="receiver", foreign_keys='ExchangeRequest.receiver_id') 