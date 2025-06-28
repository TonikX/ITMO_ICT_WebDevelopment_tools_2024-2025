from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.schemas.user_book import UserBookCreate, UserBookRead, UserBookUpdateAvailability
from app.crud.user_book import add_user_book, get_my_userbooks, update_userbook_availability, get_userbook, delete_userbook
from app.api.deps import get_db
from app.api.auth import get_current_user
from app.models.user import User
from typing import List, Optional
from app.models.book import Book
from app.models.user_book import UserBook

router = APIRouter()

@router.post("/", response_model=UserBookRead)
def add_to_library(userbook_in: UserBookCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    userbook = add_user_book(db, current_user, userbook_in)
    return UserBookRead(
        **userbook.__dict__,
        book_title=getattr(userbook.book, 'title', None),
        book_author=getattr(userbook.book, 'author', None)
    )

@router.get("/my", response_model=List[UserBookRead])
def my_library(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    userbooks = get_my_userbooks(db, current_user)
    return [UserBookRead(
        **ub.__dict__,
        book_title=getattr(ub.book, 'title', None),
        book_author=getattr(ub.book, 'author', None)
    ) for ub in userbooks]

@router.patch("/{userbook_id}/availability", response_model=UserBookRead)
def set_availability(userbook_id: int, data: UserBookUpdateAvailability, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    userbook = get_userbook(db, userbook_id)
    if not userbook:
        raise HTTPException(status_code=404, detail="UserBook not found")
    if userbook.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your book")
    userbook = update_userbook_availability(db, userbook, data.is_available)
    return UserBookRead(
        **userbook.__dict__,
        book_title=getattr(userbook.book, 'title', None),
        book_author=getattr(userbook.book, 'author', None)
    )

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_library(book_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    userbook = db.query(UserBook).filter(UserBook.book_id == book_id, UserBook.user_id == current_user.id).first()
    if not userbook:
        raise HTTPException(status_code=404, detail="UserBook not found")
    try:
        delete_userbook(db, userbook, current_user)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return None

@router.get("/search", response_model=List[UserBookRead])
def search_available_books(
    title: Optional[str] = None,
    author: Optional[str] = None,
    genre: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(UserBook).join(Book, UserBook.book_id == Book.id).filter(
        UserBook.is_available == True,
        UserBook.user_id != current_user.id
    )
    filters = []
    if title:
        filters.append(Book.title.ilike(f"%{title}%"))
    if author:
        filters.append(Book.author.ilike(f"%{author}%"))
    if genre:
        filters.append(Book.genre.ilike(f"%{genre}%"))
    if filters:
        query = query.filter(or_(*filters))
    userbooks = query.all()
    return [UserBookRead(
        **ub.__dict__,
        book_title=getattr(ub.book, 'title', None),
        book_author=getattr(ub.book, 'author', None)
    ) for ub in userbooks] 