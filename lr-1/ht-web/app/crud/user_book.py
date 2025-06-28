from sqlalchemy.orm import Session
from app.models.user_book import UserBook
from app.schemas.user_book import UserBookCreate, UserBookUpdateAvailability
from app.models.user import User
from typing import List, Optional

def add_user_book(db: Session, user: User, userbook_in: UserBookCreate) -> UserBook:
    userbook = UserBook(user_id=user.id, book_id=userbook_in.book_id, is_available=userbook_in.is_available)
    db.add(userbook)
    db.commit()
    db.refresh(userbook)
    return userbook

def get_my_userbooks(db: Session, user: User) -> List[UserBook]:
    return db.query(UserBook).filter(UserBook.user_id == user.id).all()

def update_userbook_availability(db: Session, userbook: UserBook, is_available: bool) -> UserBook:
    userbook.is_available = is_available
    db.commit()
    db.refresh(userbook)
    return userbook

def get_userbook(db: Session, userbook_id: int) -> Optional[UserBook]:
    return db.query(UserBook).filter(UserBook.id == userbook_id).first()

def delete_userbook(db: Session, userbook: UserBook, user: User) -> None:
    if userbook.user_id != user.id:
        raise PermissionError("Only the owner can delete this userbook.")
    db.delete(userbook)
    db.commit() 