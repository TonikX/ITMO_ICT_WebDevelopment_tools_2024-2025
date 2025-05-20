from fastapi import FastAPI, Depends, HTTPException, status
from typing import List
from sqlmodel import Session, select
from connection import init_db, get_session
from models import *

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()


# создать тег
@app.post("/tags/", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(tag: Tag, session: Session = Depends(get_session)):
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


# список тегов
@app.get("/tags/", response_model=List[TagRead])
def list_tags(session: Session = Depends(get_session)):
    return session.exec(select(Tag)).all()


# привязать тег к книге
@app.post("/books/{book_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def attach_tag(book_id: int, tag_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    tag  = session.get(Tag,  tag_id)
    if not (book and tag):
        raise HTTPException(404, "Book or Tag not found")
    book.tags.append(tag)
    session.add(book)
    session.commit()


# CRUD для пользователей
@app.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.get("/users/{user_id}", response_model=UserRead)
def read_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


# CRUD для книг
@app.post("/books/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def add_book(book_in: BookCreate, session: Session = Depends(get_session)):
    book = Book.model_validate(book_in)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


@app.get("/books/", response_model=List[BookRead])
def list_books(session: Session = Depends(get_session)):
    return session.exec(select(Book)).all()


# запрос на обмен книгой
@app.post("/exchange/", response_model=ExchangeRequest, status_code=status.HTTP_201_CREATED)
def request_exchange(req: ExchangeRequest, session: Session = Depends(get_session)):
    session.add(req)
    session.commit()
    session.refresh(req)
    return req


# управление запросами
@app.get("/exchange/", response_model=List[ExchangeRequestRead])
def list_exchanges(session: Session = Depends(get_session)):
    return session.exec(select(ExchangeRequest)).all()


@app.patch("/exchange/{request_id}/status", response_model=ExchangeRequest)
def update_exchange_status(
    request_id: int,
    status: RequestStatus,
    session: Session = Depends(get_session)
):
    req = session.get(ExchangeRequest, request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    req.status = status
    session.add(req)
    session.commit()
    session.refresh(req)
    return req
