from fastapi import APIRouter, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials
from models.models import Book, BookDefault, BookInfo, BookInfoDefault, Tag
from models.public_models import BookPublic, BookPatch, BookInfoPublic, TagPublic
from connection import get_session
from helpers import upd_model, get_object_by_id
from typing_extensions import TypedDict
from .auth_endpoints import auth_checker
from jwt_logic import bearer_scheme

book_router = APIRouter()

@book_router.get("/book_instance/{id}", response_model=BookPublic)
def get_book_instance(book_id: int, session=Depends(get_session)):
    return get_object_by_id(book_id, Book, session)


@book_router.post("/book_instance")
@auth_checker
async def create_book_instance(new_book: BookDefault, credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
                         session=Depends(get_session)) -> TypedDict('Response', {"status": int, "created": Book}):
    new_book = Book.model_validate(new_book)
    session.add(new_book)
    session.commit()
    session.refresh(new_book)
    return {"status": 201, "created": new_book}


@book_router.patch("/book_instance/{id}")
@auth_checker
async def update_book_instance(book_id: int, upd_book: BookPatch, credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
                         session=Depends(get_session)) -> TypedDict('Response', {"status": int, "updated": Book}):
    book = get_object_by_id(book_id, Book, session)
    upd_data = upd_book.model_dump(exclude_unset=True)
    book = upd_model(book, upd_data, session)
    return {"status": 202, "updated": book}


@book_router.get("/book_info_list")
@auth_checker
async def get_book_info_list(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
                       session=Depends(get_session)) -> list[BookInfo]:
    return session.query(BookInfo).all()


@book_router.get("/book_info/{id}", response_model=BookInfoPublic)
@auth_checker
async def get_book_info(info_id: int, credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
                       session=Depends(get_session)):
    return get_object_by_id(info_id, BookInfo, session)


@book_router.post("/book_info")
@auth_checker
async def create_book_info(book: BookInfoDefault, credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
                     session=Depends(get_session)) -> TypedDict('Response', {"status": int, "created": BookInfo}):
    book = BookInfo.model_validate(book)
    session.add(book)
    session.commit()
    session.refresh(book)
    return {"status": 201, "created": book}


@book_router.get("/book_tag/{id}", response_model=TagPublic)
@auth_checker
async def get_book_tag(tag_id: int, credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
                       session=Depends(get_session)):
    return get_object_by_id(tag_id, Tag, session)
