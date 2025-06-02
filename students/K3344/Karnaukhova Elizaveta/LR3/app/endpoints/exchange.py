from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..models import UserBook, BookExchange, ExchangeStatus
from ..models.ExchangeRequest import ExchangeRequest
from ..db import get_session
from ..schemas.exchange import ExchangeResponse, ExchangeRequestCreate, ExchangeRequestRead
from typing import List

router = APIRouter(prefix="/exchange", tags=["exchange"])


@router.post("/", response_model=ExchangeResponse)
def create_exchange_request(exchange_request: ExchangeRequestCreate, db: Session = Depends(get_session)):
    # Проверка наличия книги в библиотеке пользователя
    user_books = db.exec(select(UserBook).where(UserBook.user_profile_id == exchange_request.requester_id)).all()
    if not any(book.book_item_id == exchange_request.requested_book_id for book in user_books):
        raise HTTPException(status_code=400, detail="У вас нет запрашиваемой книги в библиотеке")

    # Проверка на уникальность книг
    if exchange_request.requested_book_id == exchange_request.offered_book_id:
        raise HTTPException(status_code=400, detail="Запрашиваемая и предлагаемая книги не могут быть одинаковыми")

    # Создание запроса на обмен
    db_request = ExchangeRequest.from_orm(exchange_request)
    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    # Преобразование в ExchangeRequestRead
    exchange_request_read = ExchangeRequestRead.from_orm(db_request)

    return ExchangeResponse(message="Запрос на обмен создан", exchange_request=exchange_request_read)


@router.get("/", response_model=List[ExchangeRequestRead])
def get_exchange_requests(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    requests = db.exec(select(ExchangeRequest).offset(skip).limit(limit)).all()
    return requests


@router.put("/{request_id}/confirm", response_model=ExchangeResponse)
def confirm_exchange_request(request_id: int, db: Session = Depends(get_session)):
    db_request = db.get(ExchangeRequest, request_id)
    if not db_request:
        raise HTTPException(status_code=404, detail="Запрос на обмен не найден")

    # Обновляем статус запроса на обмен
    db_request.status = "accepted"
    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    # Создаем запись в BookExchange
    db_exchange = BookExchange(
        exchange_request_id=db_request.id,
        user_profile_id=db_request.requester_id,  # Или другой пользователь, который подтверждает обмен
        status=ExchangeStatus.PENDING  # Установите начальный статус
    )
    db.add(db_exchange)
    db.commit()
    db.refresh(db_exchange)

    return ExchangeResponse(message="Запрос на обмен подтвержден", exchange_request=db_request)


@router.put("/{request_id}/decline", response_model=ExchangeResponse)
def decline_exchange_request(request_id: int, db: Session = Depends(get_session)):
    db_request = db.get(ExchangeRequest, request_id)
    if not db_request:
        raise HTTPException(status_code=404, detail="Запрос на обмен не найден")

    db_request.status = "declined"
    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    return ExchangeResponse(message="Запрос на обмен отклонен", exchange_request=db_request)


# @router.get("/active", response_model=List[BookExchange])
# def get_active_exchanges(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
#     exchanges = db.exec(
#         select(BookExchange).where(BookExchange.status == ExchangeStatus.PENDING).offset(skip).limit(limit)).all()
#     return exchanges
