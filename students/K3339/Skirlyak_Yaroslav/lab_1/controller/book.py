from typing import List
from fastapi import HTTPException, Depends, APIRouter, status
from sqlmodel import select, Session
from connection import get_session
from models import Book, BookIn, BookOut, CategoryOut, Category, BookCategory, Author
from contextlib import contextmanager

router = APIRouter(prefix="/books", tags=["Books"])


@contextmanager
def session_manager(session: Session):
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    finally:
        session.close()


@router.get("", response_model=List[BookOut])
def books_list(session: Session = Depends(get_session)):
    with session_manager(session):
        return session.exec(select(Book)).all()


@router.get("/{book_id}", response_model=BookOut)
def books_get(book_id: int, session: Session = Depends(get_session)):
    with session_manager(session):
        book = session.get(Book, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        return book


@router.post("", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def books_create(book: BookIn, session: Session = Depends(get_session)):
    with session_manager(session):
        author = session.get(Author, book.author_id)
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author not found"
            )

        db_book = Book.model_validate(book)
        session.add(db_book)
        session.commit()
        session.refresh(db_book)
        return db_book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def book_delete(book_id: int, session: Session = Depends(get_session)):
    with session_manager(session):
        book = session.get(Book, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        session.delete(book)
        session.commit()
        return None


@router.patch("/{book_id}", response_model=BookOut)
def book_update(
        book_id: int,
        book: BookIn,
        session: Session = Depends(get_session)
):
    with session_manager(session):
        db_book = session.get(Book, book_id)
        if not db_book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        if book.author_id:
            author = session.get(Author, book.author_id)
            if not author:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Author not found"
                )

        update_data = book.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_book, key, value)

        session.add(db_book)
        session.commit()
        session.refresh(db_book)
        return db_book


@router.get("/{book_id}/categories", response_model=List[CategoryOut])
def book_categories_list(book_id: int, session: Session = Depends(get_session)):
    with session_manager(session):
        book = session.get(Book, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        return book.categories


@router.post("/{book_id}/categories/{category_id}", response_model=BookOut)
def add_category_to_book(
        book_id: int,
        category_id: int,
        session: Session = Depends(get_session)
):
    with session_manager(session):
        book = session.get(Book, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        category = session.get(Category, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        existing = session.exec(
            select(BookCategory)
            .where(BookCategory.book_id == book_id)
            .where(BookCategory.category_id == category_id)
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category already added to this book"
            )

        book_category = BookCategory(book_id=book_id, category_id=category_id)
        session.add(book_category)
        session.commit()
        session.refresh(book)
        return book


@router.delete("/{book_id}/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_category_from_book(
        book_id: int,
        category_id: int,
        session: Session = Depends(get_session)
):
    with session_manager(session):
        book_category = session.exec(
            select(BookCategory)
            .where(BookCategory.book_id == book_id)
            .where(BookCategory.category_id == category_id)
        ).first()

        if not book_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found in this book"
            )

        session.delete(book_category)
        session.commit()
        return None