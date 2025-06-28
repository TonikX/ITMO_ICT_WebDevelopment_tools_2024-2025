from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class UserBook(Base):
    __tablename__ = "user_books"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="books")
    book = relationship("Book", back_populates="owners") 