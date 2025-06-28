from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
from datetime import datetime

class ExchangeStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    completed = "completed"

class ExchangeRequest(Base):
    __tablename__ = "exchange_requests"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sender_book_id = Column(Integer, ForeignKey("user_books.id"), nullable=True)
    receiver_book_id = Column(Integer, ForeignKey("user_books.id"), nullable=True)
    status = Column(Enum(ExchangeStatus), default=ExchangeStatus.pending, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_requests")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_requests")
    sender_book = relationship("UserBook", foreign_keys=[sender_book_id])
    receiver_book = relationship("UserBook", foreign_keys=[receiver_book_id])
    status_history = relationship("ExchangeStatusHistory", back_populates="exchange_request") 