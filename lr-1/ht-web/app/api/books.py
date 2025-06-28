from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.book import BookCreate, BookRead
from app.crud.book import get_book, get_books, create_book, delete_book
from app.api.deps import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.book import Book
from typing import List

router = APIRouter()

@router.post("/", response_model=BookRead)
def add_book(book_in: BookCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    book = create_book(db, book_in, current_user)
    return BookRead(**book.__dict__, owner_email=current_user.email)

@router.get("/", response_model=List[BookRead])
def list_books(db: Session = Depends(get_db)):
    books = get_books(db)
    return [BookRead(**b.__dict__, owner_email=getattr(b.owner, 'email', None)) for b in books]

@router.get("/search", response_model=List[BookRead])
def search_books(title: str, db: Session = Depends(get_db)):
    books = db.query(Book).filter(Book.title.ilike(f"%{title}%")).all()
    return [BookRead(**b.__dict__, owner_email=getattr(b.owner, 'email', None)) for b in books]

@router.get("/{book_id}", response_model=BookRead)
def get_book_by_id(book_id: int, db: Session = Depends(get_db)):
    book = get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return BookRead(**book.__dict__, owner_email=getattr(book.owner, 'email', None))

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_book(book_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    book = get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    try:
        delete_book(db, book, current_user)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return None 