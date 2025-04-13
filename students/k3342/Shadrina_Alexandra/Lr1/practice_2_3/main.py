from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import select

from connection import init_db, get_session
from typing_extensions import TypedDict
from typing import List
from datetime import datetime
from models import *

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"message": "Приложение работает!"}


@app.post("/book")
def add_book(book: BookCreate, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "data": BookCreate}):
    book = Book.model_validate(book)
    session.add(book)
    session.commit()
    session.refresh(book)
    return {"status": 200, "data": book}


@app.get("/books_list")
def books_list(session=Depends(get_session)):
    return session.exec(select(Book)).all()


@app.get("/book/{book_id}")
def book_get(book_id: int, session=Depends(get_session)) -> Book:
    return session.exec(select(Book).where(Book.id == book_id)).first()


@app.patch("/book{book_id}")
def book_update(book_id: int, book: BookCreate, session=Depends(get_session)) -> BookCreate:
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    book_data = book.model_dump(exclude_unset=True)
    for key, value in book_data.items():
        setattr(db_book, key, value)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@app.delete("/book/delete{book_id}")
def book_delete(book_id: int, session=Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    session.delete(book)
    session.commit()
    return {"ok": True}


@app.post("/user")
def create_user(user: UserCreate, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "data": UserCreate}):
    user = User.model_validate(user)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"status": 200, "data": user}


@app.get("/users_list")
def list_users(session=Depends(get_session)) -> List[User]:
    return session.exec(select(User)).all()


@app.get("/user/{user_id}")
def get_user(user_id: int, session=Depends(get_session)) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.delete("/user/{user_id}")
def delete_user(user_id: int, session=Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}


@app.post("/status")
def create_status(status: ExchangeStatus, session=Depends(get_session)) -> ExchangeStatus:
    session.add(status)
    session.commit()
    session.refresh(status)
    return status


@app.get("/statuses")
def list_statuses(session=Depends(get_session)) -> List[ExchangeStatus]:
    return session.exec(select(ExchangeStatus)).all()


@app.get("/status/{status_id}")
def get_status(status_id: int, session=Depends(get_session)) -> ExchangeStatus:
    status = session.get(ExchangeStatus, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")
    return status


@app.post("/library", response_model=LibraryRead)
def add_library(library: LibraryBase, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "data": LibraryBase}):
    new_entry = Library.model_validate(library)
    session.add(new_entry)
    session.commit()
    session.refresh(new_entry)
    return new_entry


@app.get("/libraries", response_model=List[LibraryRead])
def get_libraries(session=Depends(get_session)):
    return session.exec(select(Library)).all()


@app.get("/library/{library_id}", response_model=LibraryRead)
def get_library(library_id: int, session=Depends(get_session)):
    library = session.get(Library, library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library entry not found")
    return library


@app.post("/exchange", response_model=ExchangeRequestRead)
def create_exchange(req: ExchangeRequestBase, session=Depends(get_session)):
    new_req = ExchangeRequest.model_validate(req)
    new_req.request_date = datetime.utcnow()
    session.add(new_req)
    session.commit()
    session.refresh(new_req)
    return new_req


@app.get("/exchange/{req_id}", response_model=ExchangeRequestRead)
def get_exchange(req_id: int, session=Depends(get_session)):
    req = session.get(ExchangeRequest, req_id)
    if not req:
        raise HTTPException(status_code=404, detail="Exchange not found")
    return req


@app.get("/exchanges", response_model=List[ExchangeRequestRead])
def list_exchanges(session=Depends(get_session)):
    return session.exec(select(ExchangeRequest)).all()
