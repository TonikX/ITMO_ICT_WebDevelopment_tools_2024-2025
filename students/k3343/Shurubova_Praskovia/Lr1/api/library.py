from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
from sqlmodel import Session, select
from db import get_session
from models import Library, LibraryCreate, LibraryUpdate
from utils.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[Library])
def get_libraries(request: Request, session: Session = Depends(get_session)):
    get_current_user(request)
    return session.exec(select(Library)).all()


@router.get("/{library_id}", response_model=Library)
def get_library(request: Request, library_id: int, session: Session = Depends(get_session)):
    get_current_user(request)
    library = session.get(Library, library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    return library


@router.post("/create", response_model=Library)
def create_library(request: Request, library: LibraryCreate, session: Session = Depends(get_session)):
    get_current_user(request)
    db_library = Library.model_validate(library)
    session.add(db_library)
    session.commit()
    session.refresh(db_library)
    return db_library


@router.patch("/update/{library_id}", response_model=Library)
def update_library(request: Request, library_id: int, library: LibraryUpdate, session: Session = Depends(get_session)):
    get_current_user(request)
    db_library = session.get(Library, library_id)
    if not db_library:
        raise HTTPException(status_code=404, detail="Library not found")
    lib_data = library.model_dump(exclude_unset=True)
    for key, value in lib_data.items():
        setattr(db_library, key, value)
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
