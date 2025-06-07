from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from sqlalchemy.orm import selectinload
from typing import List
from app.auth.dependencies import get_current_user
from app.models import Library, LibraryBase, LibraryRead, LibraryCreate, Book, User, UserLibraryResponse, BookInfo
from app.connection import get_session

router = APIRouter(prefix="/libraries", tags=["Libraries"])


@router.post("/library", response_model=LibraryRead)
def add_library(
    library: LibraryCreate,
    session=Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    existing = session.exec(
        select(Library).where(
            Library.user_id == current_user.id,
            Library.book_id == library.book_id
        )
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="This book is already in your library")

    new_entry = Library(
        user_id=current_user.id,
        book_id=library.book_id,
        book_status=library.book_status
    )
    session.add(new_entry)
    session.commit()
    session.refresh(new_entry)
    return new_entry


@router.get("/libraries", response_model=List[LibraryRead])
def get_libraries(session=Depends(get_session)):
    return session.exec(select(Library)).all()


@router.get("/library/{library_id}", response_model=LibraryRead)
def get_library(library_id: int, session=Depends(get_session)):
    library = session.get(Library, library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library entry not found")
    return library


@router.get("/user/{user_id}/library", response_model=UserLibraryResponse)
def get_user_library(user_id: int, session=Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    libraries = session.exec(
        select(Library).where(Library.user_id == user_id).options(selectinload(Library.book))
    ).all()

    if not libraries:
        raise HTTPException(status_code=404, detail="User has no books")

    books = [
        BookInfo(
            id=entry.book.id,
            title=entry.book.title,
            author=entry.book.author,
            status=entry.book_status
        )
        for entry in libraries
    ]

    return UserLibraryResponse(
        user_id=user.id,
        username=user.username,
        email=user.email,
        books=books
    )


@router.get("/user/{user_id}/books/available", response_model=List[LibraryRead])
def get_available_books_by_user(user_id: int, session=Depends(get_session)):
    libraries = session.exec(
        select(Library).where(
            (Library.user_id == user_id) &
            (Library.book_status == "Available")
        )
    ).all()

    if not libraries:
        raise HTTPException(status_code=404, detail="User has no books")

    return libraries


@router.get("/user/{user_id}/library/search", response_model=List[LibraryRead])
def search_user_library(
    user_id: int,
    query: str = Query(..., min_length=1),
    session=Depends(get_session)
):
    stmt = (
        select(Library)
        .where(Library.user_id == user_id)
        .options(selectinload(Library.book))
        .join(Library.book)
        .where(
            (Book.title.ilike(f"%{query}%")) |
            (Book.author.ilike(f"%{query}%")) |
            (Book.genre.ilike(f"%{query}%")) |
            (Book.publisher.ilike(f"%{query}%"))
        )
    )
    results = session.exec(stmt).all()
    return results


@router.patch("/library/{library_id}")
def update_library(library_id: int, library: LibraryBase, session=Depends(get_session)):
    db_library = session.get(Library, library_id)
    if not db_library:
        raise HTTPException(status_code=404, detail="Library not found")
    for key, value in library.model_dump(exclude_unset=True).items():
        setattr(db_library, key, value)
    session.commit()
    session.refresh(db_library)
    return db_library


@router.delete("/library/{library_id}")
def delete_library(library_id: int, session=Depends(get_session)):
    lib = session.get(Library, library_id)
    if not lib:
        raise HTTPException(status_code=404, detail="Library not found")
    session.delete(lib)
    session.commit()
    return {"ok": True}
