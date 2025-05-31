import os
from datetime import datetime, timedelta
from typing import List, Dict

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import select, Session
from sqlalchemy.orm import selectinload, joinedload
import jwt
from celery_worker import parse_books_task
from celery.result import AsyncResult
from fastapi import Path
from connection import init_db, get_session
from models import User, Book, Offer, UserBook, Exchange
from schemas import (
    UserRead, UserCreate,
    BookRead, BookCreate,
    OfferRead, OfferCreate, OfferResponse,
    UserBookRead, UserBookCreate,
    ExchangeRead, ExchangeCreate, ExchangeResponse,
    ParseRequest
)

security = HTTPBearer()
app = FastAPI()

ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Получение переменных окружения из docker-compose
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
PARSER_SERVICE_URL = os.getenv("PARSER_SERVICE_URL")


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
):
    token_data = verify_token(credentials.credentials)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.exec(select(User).where(User.username == token_data["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.on_event("startup")
def on_startup():
    init_db()


# === Пользователи ===

@app.get("/users", response_model=List[UserRead])
def get_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()


@app.get("/users/me", response_model=UserRead)
def get_current_user_info(user: User = Depends(get_current_user)):
    return user


@app.get("/user/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/register")
def register_user(user_create: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.username == user_create.username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        username=user_create.username,
        email=user_create.email,
        about_me=user_create.about_me,
        created_at=datetime.utcnow().isoformat(),
    )
    new_user.set_password(user_create.password)

    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message": "User registered successfully"}


@app.post("/login")
def login(username: str, password: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not user.verify_password(password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@app.put("/users/change-password")
def change_password(
    old_password: str,
    new_password: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if not user.verify_password(old_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    user.set_password(new_password)
    session.add(user)
    session.commit()
    return {"message": "Password changed"}


# === Книги ===

@app.get("/books", response_model=List[BookRead])
def get_books(session: Session = Depends(get_session)):
    books = session.exec(select(Book)).all()
    return books


@app.get("/book/{book_id}", response_model=BookRead)
def get_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.post("/book", response_model=BookRead)
def create_book(book_create: BookCreate, session: Session = Depends(get_session)):
    new_book = Book(**book_create.dict())
    session.add(new_book)
    session.commit()
    session.refresh(new_book)
    return new_book


@app.put("/book/{book_id}", response_model=BookRead)
def update_book(book_id: int, book_update: BookCreate, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book_data = book_update.dict()
    for key, value in book_data.items():
        setattr(book, key, value)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


@app.delete("/book/{book_id}")
def delete_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    session.delete(book)
    session.commit()
    return {"detail": f"Book with id {book_id} has been deleted"}


# === Офферы (предложения) ===

@app.get("/offers", response_model=List[OfferResponse])
def get_all_offers(session: Session = Depends(get_session)):
    offers = session.exec(select(Offer)).all()
    return offers


@app.get("/offer/{offer_id}", response_model=OfferRead)
def get_offer(offer_id: int, session: Session = Depends(get_session)):
    statement = (
        select(Offer)
        .where(Offer.id == offer_id)
        .options(
            selectinload(Offer.sender),
            selectinload(Offer.receiver),
            selectinload(Offer.sender_book).selectinload(UserBook.user),
            selectinload(Offer.sender_book).selectinload(UserBook.book),
            selectinload(Offer.receiver_book).selectinload(UserBook.user),
            selectinload(Offer.receiver_book).selectinload(UserBook.book),
            selectinload(Offer.exchange),
        )
    )
    offer = session.exec(statement).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return offer


@app.post("/offer", response_model=OfferRead)
def create_offer(offer_create: OfferCreate, session: Session = Depends(get_session)):
    new_offer = Offer(
        **offer_create.dict(),
        created_at=datetime.utcnow().isoformat(),
    )
    session.add(new_offer)
    session.commit()
    session.refresh(new_offer)
    return new_offer


@app.put("/offer/{offer_id}", response_model=OfferRead)
def update_offer(offer_id: int, offer_update: OfferCreate, session: Session = Depends(get_session)):
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    offer_data = offer_update.dict()
    for key, value in offer_data.items():
        setattr(offer, key, value)

    session.add(offer)
    session.commit()
    session.refresh(offer)
    return offer


@app.delete("/offer/{offer_id}")
def delete_offer(offer_id: int, session: Session = Depends(get_session)):
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    session.delete(offer)
    session.commit()
    return {"detail": f"Offer with id {offer_id} has been deleted"}


# === UserBook ===

@app.get("/user_books", response_model=List[UserBookRead])
def get_user_books(session: Session = Depends(get_session)):
    statement = (
        select(UserBook)
        .options(
            selectinload(UserBook.user),
            selectinload(UserBook.book),
        )
    )
    user_books = session.exec(statement).all()
    return user_books


@app.get("/user_book/{user_book_id}", response_model=UserBookRead)
def get_user_book(user_book_id: int, session: Session = Depends(get_session)):
    statement = (
        select(UserBook)
        .where(UserBook.id == user_book_id)
        .options(
            selectinload(UserBook.user),
            selectinload(UserBook.book),
        )
    )
    user_book = session.exec(statement).first()
    if not user_book:
        raise HTTPException(status_code=404, detail="UserBook not found")
    return user_book


@app.post("/user_book", response_model=UserBookRead)
def create_user_book(user_book_create: UserBookCreate, session: Session = Depends(get_session)):
    new_user_book = UserBook(**user_book_create.dict())
    session.add(new_user_book)
    session.commit()
    session.refresh(new_user_book)
    return new_user_book


@app.put("/user_book/{user_book_id}", response_model=UserBookRead)
def update_user_book(user_book_id: int, user_book_update: UserBookCreate, session: Session = Depends(get_session)):
    user_book = session.get(UserBook, user_book_id)
    if not user_book:
        raise HTTPException(status_code=404, detail="UserBook not found")

    update_data = user_book_update.dict()
    for key, value in update_data.items():
        setattr(user_book, key, value)

    session.add(user_book)
    session.commit()
    session.refresh(user_book)
    return user_book


@app.delete("/user_book/{user_book_id}")
def delete_user_book(user_book_id: int, session: Session = Depends(get_session)):
    user_book = session.get(UserBook, user_book_id)
    if not user_book:
        raise HTTPException(status_code=404, detail="UserBook not found")
    session.delete(user_book)
    session.commit()
    return {"detail": f"UserBook with id {user_book_id} has been deleted"}


# === Обмены (Exchanges) ===

@app.get("/exchanges", response_model=List[ExchangeResponse])
def get_exchanges(session: Session = Depends(get_session)):
    statement = (
        select(Exchange)
        .options(
            selectinload(Exchange.offer_sender).selectinload(Offer.sender),
            selectinload(Exchange.offer_receiver).selectinload(Offer.receiver),
        )
    )
    exchanges = session.exec(statement).all()
    return exchanges


@app.get("/exchange/{exchange_id}", response_model=ExchangeRead)
def get_exchange(exchange_id: int, session: Session = Depends(get_session)):
    exchange = session.get(Exchange, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
    return exchange


@app.post("/exchange", response_model=ExchangeRead)
def create_exchange(exchange_create: ExchangeCreate, session: Session = Depends(get_session)):
    new_exchange = Exchange(**exchange_create.dict())
    session.add(new_exchange)
    session.commit()
    session.refresh(new_exchange)
    return new_exchange


@app.put("/exchange/{exchange_id}", response_model=ExchangeRead)
def update_exchange(exchange_id: int, exchange_update: ExchangeCreate, session: Session = Depends(get_session)):
    exchange = session.get(Exchange, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")

    update_data = exchange_update.dict()
    for key, value in update_data.items():
        setattr(exchange, key, value)

    session.add(exchange)
    session.commit()
    session.refresh(exchange)
    return exchange


@app.delete("/exchange/{exchange_id}")
def delete_exchange(exchange_id: int, session: Session = Depends(get_session)):
    exchange = session.get(Exchange, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
    session.delete(exchange)
    session.commit()
    return {"detail": f"Exchange with id {exchange_id} has been deleted"}



@app.post("/parse")
async def parse_books(request: ParseRequest):
    task = parse_books_task.delay(request.url, request.genre)  # ставим в очередь
    return {"task_id": task.id, "status": "Processing"}


@app.get("/parse/status/{task_id}")
async def get_parse_status(task_id: str = Path(...)):
    task_result = AsyncResult(task_id, app=parse_books_task.app)
    if task_result.state == "PENDING":
        return {"task_id": task_id, "status": "Pending"}
    elif task_result.state == "SUCCESS":
        return {"task_id": task_id, "status": "Success", "result": task_result.result}
    elif task_result.state == "FAILURE":
        return {"task_id": task_id, "status": "Failure", "error": str(task_result.result)}
    else:
        return {"task_id": task_id, "status": task_result.state}