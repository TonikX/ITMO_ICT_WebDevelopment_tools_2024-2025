from typing import List
from fastapi import HTTPException, Depends, APIRouter, status
from sqlmodel import select, Session
from connection import get_session
from models import Book, User, BookCopy, UserOut, UserIn
from contextlib import contextmanager

router = APIRouter(prefix="/book_copy", tags=["Book Copy"])


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


@router.get("", response_model=List[BookCopy])
def get_all_book_copies(session: Session = Depends(get_session)):
    with session_manager(session):
        return session.exec(select(BookCopy)).all()


@router.get("/{user_id}/{book_id}", response_model=List[BookCopy])
def get_book_copies_by_user_and_book(
        user_id: int,
        book_id: int,
        session: Session = Depends(get_session)
):
    with session_manager(session):
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        book = session.get(Book, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        book_copies = session.exec(
            select(BookCopy)
            .where(BookCopy.user_id == user_id)
            .where(BookCopy.book_id == book_id)
        ).all()

        return book_copies


@router.post("/{user_id}/{book_id}", response_model=BookCopy, status_code=status.HTTP_201_CREATED)
def create_book_copy(
        user_id: int,
        book_id: int,
        session: Session = Depends(get_session)
):
    with session_manager(session):
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        book = session.get(Book, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        book_copy = BookCopy(book_id=book_id, user_id=user_id)
        session.add(book_copy)
        session.commit()
        session.refresh(book_copy)

        return book_copy


@router.delete("/{copy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book_copy(
        copy_id: int,
        session: Session = Depends(get_session)
):
    with session_manager(session):
        book_copy = session.get(BookCopy, copy_id)
        if not book_copy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book copy not found"
            )

        session.delete(book_copy)
        session.commit()
        return None