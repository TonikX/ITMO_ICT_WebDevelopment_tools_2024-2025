from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, or_

from ..connection import get_session
from labs.Lr1.core.dependencies import get_current_user
from ..core.auth import hash_password
from ..models import User, UserCreate, UserRead, UserUpdate, Book, BookRead, Library, LibraryUpdate, UserBookRead, \
    ExchangeRequest, StatusExchangeRequest

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserRead])
def read_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserRead)
def update_current_user(update_data: UserUpdate, current_user: User = Depends(get_current_user),
                        session: Session = Depends(get_session)):
    user_data = update_data.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        hashed_password = hash_password(user_data["password"])
        extra_data["hashed_password"] = hashed_password
    if "email" in user_data:
        existing_email = session.exec(
            select(User).where(User.email == user_data["email"])
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=400, detail="User with this email already exists"
            )
    current_user.sqlmodel_update(user_data, update=extra_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.get("/me/books", response_model=list[BookRead])
def read_current_user_books(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    books = session.exec(select(Book).join(Library).where(Library.user_id == current_user.id)).all()
    return books


@router.get("/{user_id}/books", response_model=list[BookRead])
def read_user_books(user_id: int, session: Session = Depends(get_session)):
    books = session.exec(select(Book).join(Library).where(Library.user_id == user_id)).all()
    return books


@router.post("/me/books", status_code=status.HTTP_201_CREATED)
def add_book_to_current_user(book_id: int, session: Session = Depends(get_session),
                             current_user: User = Depends(get_current_user)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    existing_entry = session.exec(
        select(Book).join(Library).where(Library.user_id == current_user.id, Library.book_id == book_id)).first()
    if existing_entry:
        raise HTTPException(status_code=400, detail="This book is already in the user's library")
    library_entry = Library(user_id=current_user.id, book_id=book_id)
    session.add(library_entry)
    session.commit()
    return {"message": "The book has been added to the user's resource"}


@router.patch("/me/books/{book_id}", response_model=UserBookRead)
def update_book_availability(update_data: LibraryUpdate, book_id: int, session: Session = Depends(get_session),
                             current_user: User = Depends(get_current_user)):
    user_book = session.exec(
        select(Library).where(Library.user_id == current_user.id, Library.book_id == book_id)).first()
    if not user_book:
        raise HTTPException(status_code=404, detail="Book not found in your library")

    exchange_exists = session.exec(
        select(ExchangeRequest).where(
            ExchangeRequest.status == StatusExchangeRequest.pending,
            or_(
                (ExchangeRequest.offered_book_id == book_id) & (ExchangeRequest.requester_id == current_user.id),
                (ExchangeRequest.requested_book_id == book_id) & (ExchangeRequest.owner_id == current_user.id),
            )
        )
    ).first()

    if exchange_exists:
        raise HTTPException(status_code=400, detail="This book is involved in an active exchange request")

    user_book.sqlmodel_update(update_data)
    session.add(user_book)
    session.commit()
    session.refresh(user_book)
    return UserBookRead(
        id=user_book.book.id,
        title=user_book.book.title,
        author=user_book.book.author,
        description=user_book.book.description,
        isbn=user_book.book.isbn,
        is_available=user_book.is_available
    )


@router.delete("/me/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_book_from_current_user(book_id: int, session: Session = Depends(get_session),
                                  current_user: User = Depends(get_current_user)):
    entry = session.get(Library, (current_user.id, book_id))
    if not entry:
        raise HTTPException(status_code=404, detail="The book was not found in the user's library")
    session.delete(entry)
    session.commit()
    return {"ok": True}


@router.get("/{user_id}", response_model=UserRead)
def read_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: int, user_update: UserUpdate, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user_update.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}
