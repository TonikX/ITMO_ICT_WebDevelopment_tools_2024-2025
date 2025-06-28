from sqlalchemy.orm import Session
from app.models.book import Book
from app.schemas.book import BookCreate
from app.models.user import User
from typing import Optional, List

def get_book(db: Session, book_id: int) -> Optional[Book]:
    return db.query(Book).filter(Book.id == book_id).first()

def get_books(db: Session, skip: int = 0, limit: int = 100) -> List[Book]:
    return db.query(Book).offset(skip).limit(limit).all()

def create_book(db: Session, book_in: BookCreate, owner: User) -> Book:
    db_book = Book(**book_in.dict(), owner_id=owner.id)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def delete_book(db: Session, book: Book, user: User) -> None:
    if book.owner_id != user.id:
        raise PermissionError("Only the owner can delete this book.")
    db.delete(book)
    db.commit() 