from fastapi import APIRouter, HTTPException, Depends
from typing import List
from starlette.requests import Request
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from app.db import get_session
from app.models.models import Exchange, ExchangeCreate, ExchangeUpdate, Book, BookStatus, ExchangeRequest, RequestStatus, \
    ExchangeInfo
from app.utils.auth import get_current_user
from datetime import datetime

router = APIRouter()


@router.get("/", response_model=List[ExchangeInfo])
def get_exchanges(request: Request, session: Session = Depends(get_session)):
    get_current_user(request)

    exchanges = session.exec(
        select(Exchange)
        .options(
            selectinload(Exchange.book),
            selectinload(Exchange.sender),
            selectinload(Exchange.receiver),
        )
    ).all()

    return exchanges


@router.get("/{exchange_id}", response_model=ExchangeInfo)
def get_exchange(request: Request, exchange_id: int, session: Session = Depends(get_session)):
    get_current_user(request)

    exchange = session.exec(
        select(Exchange)
        .where(Exchange.id == exchange_id)
        .options(
            selectinload(Exchange.book),
            selectinload(Exchange.sender),
            selectinload(Exchange.receiver),
        )
    ).first()

    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")

    return exchange


@router.post("/create", response_model=ExchangeInfo)
def create_exchange(request: Request, exchange: ExchangeCreate, session: Session = Depends(get_session)):
    get_current_user(request)
    req = session.get(ExchangeRequest, exchange.request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Exchange request not found")

    if req.status != RequestStatus.accepted:
        raise HTTPException(status_code=400, detail="Exchange request must be accepted before creating an exchange")

    book = session.get(Book, exchange.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.status != BookStatus.available:
        raise HTTPException(status_code=400, detail="Book is not available for exchange")

    book.status = BookStatus.exchanged

    db_exchange = Exchange(
        request_id=exchange.request_id,
        book_id=exchange.book_id,
        sender_id=exchange.sender_id,
        receiver_id=exchange.receiver_id,
        start_date=exchange.start_date or datetime.utcnow(),
        end_date=exchange.end_date
    )

    session.add(db_exchange)
    session.commit()
    session.refresh(db_exchange)

    return db_exchange


@router.patch("/update/{exchange_id}", response_model=ExchangeInfo)
def update_exchange(request: Request, exchange_id: int, exchange: ExchangeUpdate,
                    session: Session = Depends(get_session)):
    current_user = get_current_user(request)

    db_exchange = session.get(Exchange, exchange_id)
    if not db_exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")

    if int(current_user["id"]) != int(db_exchange.sender_id) and int(current_user["id"]) != int(db_exchange.receiver_id):
        raise HTTPException(status_code=403, detail="Only the creator or the receiver can update the request")

    exchange_data = exchange.model_dump(exclude_unset=True)
    for key, value in exchange_data.items():
        setattr(db_exchange, key, value)

    session.commit()
    session.refresh(db_exchange)

    return db_exchange


@router.delete("/delete/{exchange_id}")
def delete_exchange(request: Request, exchange_id: int, session: Session = Depends(get_session)):
    get_current_user(request)
    exchange = session.get(Exchange, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")

    book = session.get(Book, exchange.book_id)
    if book:
        book.status = BookStatus.available

    session.delete(exchange)
    session.commit()
    return {"message": "Exchange deleted"}
