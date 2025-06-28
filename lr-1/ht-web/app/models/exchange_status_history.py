from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
from app.models.exchange_request import ExchangeStatus

class ExchangeStatusHistory(Base):
    __tablename__ = "exchange_status_history"

    id = Column(Integer, primary_key=True, index=True)
    exchange_request_id = Column(Integer, ForeignKey("exchange_requests.id"), nullable=False)
    status = Column(Enum(ExchangeStatus), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)

    exchange_request = relationship("ExchangeRequest", back_populates="status_history") 