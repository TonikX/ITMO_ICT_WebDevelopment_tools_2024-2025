from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    isbn = Column(String(20), unique=True, nullable=True)
    genre = Column(String(50), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owners = relationship("UserBook", back_populates="book")
    owner = relationship("User") 