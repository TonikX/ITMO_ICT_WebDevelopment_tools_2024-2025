from fastapi import APIRouter, HTTPException, Depends
from starlette.requests import Request

from typing import List
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from app.db import get_session
from app.models.models import Library, LibraryCreate, LibraryUpdate, LibraryInfo, LibraryBook, BookInfo, UserPublic
from app.utils.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[LibraryInfo])
def get_libraries(request: Request, session: Session = Depends(get_session)):
    get_current_user(request)
    libraries = session.exec(
        select(Library)
        .options(
            selectinload(Library.user),
            selectinload(Library.books).selectinload(LibraryBook.book)
        )
    ).all()

    return [
        LibraryInfo(
            id=lib.id,
            name=lib.name,
            user=UserPublic.model_validate(lib.user),
            books=[BookInfo.model_validate(lb.book) for lb in lib.books]
        )
        for lib in libraries
    ]


@router.get("/{library_id}", response_model=LibraryInfo)
def get_library(request: Request, library_id: int, session: Session = Depends(get_session)):
    get_current_user(request)
    library = session.exec(
        select(Library)
        .where(Library.id == library_id)
        .options(
            selectinload(Library.user),
            selectinload(Library.books).selectinload(LibraryBook.book)
        )
    ).first()

    if not library:
        raise HTTPException(status_code=404, detail="Library not found")

    return LibraryInfo(
        id=library.id,
        name=library.name,
        user=UserPublic.model_validate(library.user),
        books=[BookInfo.model_validate(lb.book) for lb in library.books]
    )


@router.post("/create", response_model=LibraryInfo)
def create_library(library: LibraryCreate, session: Session = Depends(get_session)):
    new_library = Library(
        name=library.name,
        user_id=library.user_id
    )
    session.add(new_library)
    session.commit()
    session.refresh(new_library)

    for book_id in library.book_ids:
        link = LibraryBook(
            library_id=new_library.id,
            book_id=book_id
        )
        session.add(link)

    session.commit()

    session.refresh(new_library)
    new_library = session.exec(
        select(Library)
        .where(Library.id == new_library.id)
        .options(
            selectinload(Library.user),
            selectinload(Library.books).selectinload(LibraryBook.book)
        )
    ).first()

    return LibraryInfo(
        id=new_library.id,
        name=new_library.name,
        user=UserPublic.model_validate(new_library.user),
        books=[BookInfo.model_validate(lb.book) for lb in new_library.books]
    )


@router.patch("/update/{library_id}", response_model=LibraryInfo)
def update_library(request: Request, library_id: int, library: LibraryUpdate, session: Session = Depends(get_session)):
    current_user = get_current_user(request)
    db_library = session.get(Library, library_id)
    if not db_library:
        raise HTTPException(status_code=404, detail="Library not found")

    if db_library.user_id != int(current_user["id"]):
        raise HTTPException(status_code=403, detail="You can only update your own libraries")

    lib_data = library.model_dump(exclude_unset=True)

    for key, value in lib_data.items():
        if key != "books":
            setattr(db_library, key, value)

    if library.books is not None:
        current_book_ids = {book.book_id for book in db_library.books}

        for book_id in library.books:
            if book_id not in current_book_ids:
                new_book = LibraryBook(library_id=db_library.id, book_id=book_id)
                session.add(new_book)

        for book in db_library.books:
            if book.book_id not in library.books:
                session.delete(book)

    session.commit()
    session.refresh(db_library)
    return db_library


@router.delete("/delete/{library_id}")
def delete_library(request: Request, library_id: int, session: Session = Depends(get_session)):
    get_current_user(request)
    library = session.get(Library, library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    session.delete(library)
    session.commit()
    return {"message": "Library deleted"}
