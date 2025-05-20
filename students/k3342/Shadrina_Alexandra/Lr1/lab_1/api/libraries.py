from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing_extensions import TypedDict
from typing import List
from models import Library, LibraryBase, LibraryRead
from connection import get_session

router = APIRouter(prefix="/libraries", tags=["Libraries"])


@router.post("/library", response_model=LibraryRead)
def add_library(library: LibraryBase, session=Depends(get_session)) -> TypedDict('Response', {"status": int,
                                                                                              "data": LibraryBase}):
    new_entry = Library.model_validate(library)
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


@router.get("/user/{user_id}/library")
def get_user_library(user_id: int, session=Depends(get_session)):
    return session.exec(select(Library).where(Library.user_id == user_id)).all()


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

