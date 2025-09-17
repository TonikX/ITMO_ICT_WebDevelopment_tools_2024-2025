from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.api.controllers.userbook_controller import (
    create_user_book, get_user_books, get_user_book, update_user_book, delete_user_book
)
from pg.schemas.schema import UserBookCreate, UserBookRead
from database import get_session

router = APIRouter(prefix="/userbooks", tags=["userbooks"])


@router.post("/", response_model=UserBookRead)
def api_create_user_book(ub_in: UserBookCreate, session: Session = Depends(get_session)):
    return create_user_book(session, ub_in)


@router.get("/", response_model=List[UserBookRead])
def api_get_user_books(session: Session = Depends(get_session)):
    return get_user_books(session)


@router.get("/{ub_id}", response_model=UserBookRead)
def api_get_user_book(ub_id: int, session: Session = Depends(get_session)):
    return get_user_book(session, ub_id)


@router.put("/{ub_id}", response_model=UserBookRead)
def api_update_user_book(ub_id: int, ub_in: UserBookCreate, session: Session = Depends(get_session)):
    return update_user_book(session, ub_id, ub_in)


@router.delete("/{ub_id}")
def api_delete_user_book(ub_id: int, session: Session = Depends(get_session)):
    return delete_user_book(session, ub_id)
