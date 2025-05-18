from fastapi import Depends, HTTPException, APIRouter
from ..db.connection import get_session
from sqlmodel import select

from ..models.book import Book
from ..models.profile import Profile
from ..models.profileLibrary import ProfileLibrary
from ..schemas.profileLibrary import ProfileLibraryRead

router = APIRouter()


@router.get("/profiles/{profile_id}/library", response_model=ProfileLibraryRead)
def get_profile_library(profile_id: int, session=Depends(get_session)):
    library = session.exec(
        select(ProfileLibrary).where(ProfileLibrary.profile_id == profile_id)
    ).first()

    if library is None:
        raise HTTPException(status_code=404, detail="Library not found")

    books = session.exec(select(Book).where(Book.profile_library_id == library.id)).all()
    owner = session.get(Profile, library.profile_id)

    return ProfileLibraryRead(id=library.id, owner=owner, books=books)


# Отчистка библиотеки от всех книг
@router.delete("/profiles/{profile_id}/library/clear")
def clear_profile_library(profile_id: int, session=Depends(get_session)):
    library = session.exec(
        select(ProfileLibrary)
        .where(ProfileLibrary.profile_id == profile_id)
    ).first()

    if not library:
        raise HTTPException(
            status_code=404,
            detail="Library not found"
        )

    books = session.exec(
        select(Book)
        .where(Book.profile_library_id == library.id)
    ).all()

    for book in books:
        session.delete(book)

    session.commit()

    return {"status": "success", "deleted_books": len(books)}
