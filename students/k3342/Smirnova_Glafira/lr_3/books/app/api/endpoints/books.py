from fastapi import APIRouter, Depends, HTTPException

from app.schemas.info import MessageResponse
from app.services.book_service import add_book, edit_book, remove_book, remove_ownership, set_book_genres, \
    get_user_books
from app.api.dependencies.auth import get_current_user
from app.db.session import get_session
from app.api.dependencies.ownership import get_current_ownership, is_original_owner
from sqlmodel import Session
from app.schemas.book import *
from app.models import Book

router = APIRouter()

@router.post("/", response_model=BookRead, status_code=201)
def create_book(
    book_create: BookCreate,
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Book:
    """Создает книгу в личной библиотеке."""
    return add_book(book_create, user_id, session)


@router.patch("/{book_id}", response_model=BookRead)
def update_book(
        book_id: int,
        book_update: BookUpdate,
        _ = Depends(get_current_ownership),
        is_original=Depends(is_original_owner),
        session: Session = Depends(get_session)
)-> Book:
    """
    Обновляет книгу.
    Доступно лишь первым владельцам книги.
    """
    if not is_original:
        raise HTTPException(status_code=400, detail="Only the original owner can update the book")
    return edit_book(book_id, book_update, session)

@router.delete("/{book_id}", response_model=MessageResponse)
def delete_book(
    book_id: int,
    ownership=Depends(get_current_ownership),
    is_original=Depends(is_original_owner),
    session: Session = Depends(get_session)
) -> MessageResponse:
    """
    Удаляет книгу из личной библиотеки, а также её оффер.
    """
    if is_original:
        remove_book(book_id, session)
    else:
        remove_ownership(book_id, ownership.user_id, session)

    return MessageResponse(message="Deleted successfully")


@router.get("/{book_id}", response_model=BookFull)
def retrieve_book(
        book_id: int,
        _ = Depends(get_current_ownership),
        session: Session = Depends(get_session)
)-> Book:
    """Возвращает книгу по ID."""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book

@router.get("/", response_model=list[BookFull])
def retrieve_my_books(
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
)-> list[Book]:
    """Возвращает список книг, которыми пользователь владеет в данный момент."""
    return get_user_books(user_id, session)

@router.patch("/{book_id}/genres", response_model=MessageResponse)
def update_book_genres(
    book_id: int,
    genres_update: BookGenresUpdate,
    _ = Depends(get_current_ownership),
    session: Session = Depends(get_session)
) -> MessageResponse:
    """Устанавливает жанры для книги (заменяет текущие)."""
    set_book_genres(book_id, genres_update, session)
    return MessageResponse(message="Genres updated")