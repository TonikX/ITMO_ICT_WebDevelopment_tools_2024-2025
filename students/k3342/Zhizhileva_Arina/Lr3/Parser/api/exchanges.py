from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from db import get_session
from models import ExchangeRequest, Exchange, UserBook, User
from schemas.exchange import (
    ExchangeRequestCreate,
    ExchangeRequestRead,
    ExchangeRequestUpdate,
    ExchangeCreate,
    ExchangeRead,
    ExchangeUpdate
)
from api.dependencies import get_current_user

router = APIRouter(prefix="/exchanges", tags=["exchanges"])


# ExchangeRequest CRUD
@router.post("/requests/", response_model=ExchangeRequestRead)
def create_exchange_request(
        request: ExchangeRequestCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    # Проверяем, что книги существуют и принадлежат соответствующим пользователям
    sender_book = session.get(UserBook, request.sender_book_id)
    if not sender_book:
        raise HTTPException(status_code=404, detail="Sender book not found")
    if sender_book.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not your book")

    desired_book = session.get(UserBook, request.desired_book_id)
    if not desired_book:
        raise HTTPException(status_code=404, detail="Desired book not found")
    if desired_book.user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="Cannot request your own book")

    # Проверяем, что книга доступна для обмена
    if desired_book.status != "доступна":
        raise HTTPException(status_code=400, detail="Desired book is not available")

    db_request = ExchangeRequest.from_orm(request, update={"sender_id": current_user.user_id})
    session.add(db_request)
    session.commit()
    session.refresh(db_request)
    return db_request


@router.get("/requests/", response_model=List[ExchangeRequestRead])
def read_exchange_requests(
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    requests = session.exec(
        select(ExchangeRequest)
        .where(
            (ExchangeRequest.sender_id == current_user.user_id) |
            (ExchangeRequest.receiver_id == current_user.user_id)
        )
        .offset(skip)
        .limit(limit)
    ).all()
    return requests


@router.patch("/requests/{request_id}", response_model=ExchangeRequestRead)
def update_exchange_request(
        request_id: int,
        request: ExchangeRequestUpdate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    db_request = session.get(ExchangeRequest, request_id)
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Только получатель может обновлять статус запроса
    if db_request.receiver_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    request_data = request.dict(exclude_unset=True)
    for key, value in request_data.items():
        setattr(db_request, key, value)

    session.add(db_request)
    session.commit()
    session.refresh(db_request)

    # Если запрос принят, создаем обмен
    if db_request.status == "accepted":
        exchange = Exchange(
            request_id=db_request.request_id,
            completion_status="в процессе"
        )
        session.add(exchange)
        session.commit()

    return db_request


# Exchange CRUD
@router.get("/", response_model=List[ExchangeRead])
def read_exchanges(
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    exchanges = session.exec(
        select(Exchange)
        .join(ExchangeRequest)
        .where(
            (ExchangeRequest.sender_id == current_user.user_id) |
            (ExchangeRequest.receiver_id == current_user.user_id)
        )
        .offset(skip)
        .limit(limit)
    ).all()
    return exchanges


@router.patch("/{exchange_id}", response_model=ExchangeRead)
def update_exchange(
        exchange_id: int,
        exchange: ExchangeUpdate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    db_exchange = session.get(Exchange, exchange_id)
    if not db_exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")

    # Получаем связанный запрос
    request = session.get(ExchangeRequest, db_exchange.request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Проверяем, что текущий пользователь участвует в обмене
    if current_user.user_id not in [request.sender_id, request.receiver_id]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    exchange_data = exchange.dict(exclude_unset=True)
    for key, value in exchange_data.items():
        setattr(db_exchange, key, value)

    session.add(db_exchange)
    session.commit()
    session.refresh(db_exchange)
    return db_exchange