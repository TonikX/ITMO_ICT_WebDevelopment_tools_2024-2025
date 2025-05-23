from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

import app.schemas as schemas
import app.crud as crud
from app.database import get_session
from app.routers.auth import authenticate_request

router = APIRouter(
    prefix="/books",
    tags=["books"],
    dependencies=[Depends(authenticate_request)],
)

@router.post("/tags", response_model=schemas.TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(
    tc: schemas.TagCreate,
    db: Session = Depends(get_session),
):
    return crud.create_tag(db, tc.name)

@router.get("/tags", response_model=List[schemas.TagRead])
def list_tags(db: Session = Depends(get_session)):
    return crud.get_tags(db)

@router.get("/tags/{tag_id}", response_model=schemas.TagRead)
def get_tag(tag_id: int, db: Session = Depends(get_session)):
    tag = crud.get_tag(db, tag_id)
    if not tag:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    return tag

@router.patch("/tags/{tag_id}", response_model=schemas.TagRead)
def update_tag(tag_id: int, upd: schemas.TagUpdate, db: Session = Depends(get_session)):
    return crud.update_tag(db, tag_id, upd)

@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_session)):
    crud.delete_tag(db, tag_id)


@router.post("/info", response_model=schemas.BookInfoRead, status_code=status.HTTP_201_CREATED)
def create_info(
    bi: schemas.BookInfoCreate,
    db: Session = Depends(get_session),
):
    return crud.create_bookinfo(db, bi)

@router.get("/info", response_model=List[schemas.BookInfoRead])
def list_info(db: Session = Depends(get_session)):
    return crud.get_bookinfos(db)

@router.get("/info/{info_id}", response_model=schemas.BookInfoRead)
def get_info(info_id: int, db: Session = Depends(get_session)):
    info = crud.get_bookinfo(db, info_id)
    if not info:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    return info

@router.patch("/info/{info_id}", response_model=schemas.BookInfoRead)
def update_info(info_id: int, upd: schemas.BookInfoUpdate, db: Session = Depends(get_session)):
    return crud.update_bookinfo(db, info_id, upd)

@router.delete("/info/{info_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_info(info_id: int, db: Session = Depends(get_session)):
    crud.delete_bookinfo(db, info_id)


@router.post("/", response_model=schemas.BookRead, status_code=status.HTTP_201_CREATED)
def create_book(bc: schemas.BookCreate, db: Session = Depends(get_session)):
    return crud.create_book(db, bc)

@router.get("/", response_model=List[schemas.BookRead])
def list_books(
    title: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    tag_id: Optional[int] = Query(None),
    db: Session = Depends(get_session),
):
    return crud.get_books(db, title, author, tag_id)

@router.get("/{book_id}", response_model=schemas.BookRead)
def get_book(book_id: int, db: Session = Depends(get_session)):
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    return book

@router.patch("/{book_id}", response_model=schemas.BookRead)
def update_book(book_id: int, upd: schemas.BookUpdate, db: Session = Depends(get_session)):
    return crud.update_book(db, book_id, upd)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_session)):
    crud.delete_book(db, book_id)