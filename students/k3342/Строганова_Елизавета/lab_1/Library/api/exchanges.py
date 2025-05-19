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


# CRUD для запросов на обмен
@router.post("/requests/", response_model=ExchangeRequestRead)
def add_exchange_request(
        exchange_request: ExchangeRequestCreate,
        db: Session = Depends(get_session),
        active_user: User = Depends(get_current_user)
):
    owner_book = db.get(UserBook, exchange_request.sender_book_id)
    if not owner_book:
        raise HTTPException(status_code=404, detail="Sender book not found")
    if owner_book.user_id != active_user.user_id:
        raise HTTPException(status_code=403, detail="You do not own this book")

    target_book = db.get(UserBook, exchange_request.desired_book_id)
    if not target_book:
        raise HTTPException(status_code=404, detail="Desired book not found")
    if target_book.user_id == active_user.user_id:
        raise HTTPException(status_code=400, detail="Cannot request your own book")

    if target_book.status != "доступна":
        raise HTTPException(status_code=400, detail="Desired book is not available for exchange")

    new_request = ExchangeRequest.from_orm(exchange_request, update={"sender_id": active_user.user_id})
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request


@router.get("/requests/", response_model=List[ExchangeRequestRead])
def get_exchange_requests(
        offset: int = 0,
        limit: int = 100,
        db: Session = Depends(get_session),
        active_user: User = Depends(get_current_user)
):
    query = select(ExchangeRequest).where(
        (ExchangeRequest.sender_id == active_user.user_id) |
        (ExchangeRequest.receiver_id == active_user.user_id)
    ).offset(offset).limit(limit)
    requests_list = db.exec(query).all()
    return requests_list


@router.patch("/requests/{req_id}", response_model=ExchangeRequestRead)
def modify_exchange_request(
        req_id: int,
        request_update: ExchangeRequestUpdate,
        db: Session = Depends(get_session),
        active_user: User = Depends(get_current_user)
):
    existing_request = db.get(ExchangeRequest, req_id)
    if not existing_request:
        raise HTTPException(status_code=404, detail="Request not found")

    if existing_request.receiver_id != active_user.user_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    update_data = request_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing_request, field, value)

    db.add(existing_request)
    db.commit()
    db.refresh(existing_request)

    if existing_request.status == "accepted":
        new_exchange = Exchange(
            request_id=existing_request.request_id,
            completion_status="в процессе"
        )
        db.add(new_exchange)
        db.commit()

    return existing_request


# CRUD для обменов
@router.get("/", response_model=List[ExchangeRead])
def list_exchanges(
        offset: int = 0,
        limit: int = 100,
        db: Session = Depends(get_session),
        active_user: User = Depends(get_current_user)
):
    query = (
        select(Exchange)
        .join(ExchangeRequest)
        .where(
            (ExchangeRequest.sender_id == active_user.user_id) |
            (ExchangeRequest.receiver_id == active_user.user_id)
        )
        .offset(offset)
        .limit(limit)
    )
    exchange_list = db.exec(query).all()
    return exchange_list


@router.patch("/{exchange_id}", response_model=ExchangeRead)
def modify_exchange(
        exchange_id: int,
        exchange_update: ExchangeUpdate,
        db: Session = Depends(get_session),
        active_user: User = Depends(get_current_user)
):
    existing_exchange = db.get(Exchange, exchange_id)
    if not existing_exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")

    related_request = db.get(ExchangeRequest, existing_exchange.request_id)
    if not related_request:
        raise HTTPException(status_code=404, detail="Related request not found")

    if active_user.user_id not in [related_request.sender_id, related_request.receiver_id]:
        raise HTTPException(status_code=403, detail="Permission denied")

    updates = exchange_update.dict(exclude_unset=True)
    for attr, val in updates.items():
        setattr(existing_exchange, attr, val)

    db.add(existing_exchange)
    db.commit()
    db.refresh(existing_exchange)
    return existing_exchange
