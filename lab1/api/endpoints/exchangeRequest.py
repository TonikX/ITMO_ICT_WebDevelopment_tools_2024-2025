from typing import List
from fastapi import HTTPException, Depends, APIRouter
from sqlmodel import select, delete
from api.models.connection import get_session
from api.models.models import ExchangeRequest
from api.schemas.exchange_request_schemas import ExchangeRequestResponse, ExchangeRequestCreate, \
    ExchangeRequestUpdateStatus

exchange_request_router = APIRouter()


@exchange_request_router.post("/exchange_request_post", response_model=ExchangeRequestResponse)
def genre_post(exchange_request: ExchangeRequestCreate, session=Depends(get_session)):
    genre_db = ExchangeRequest(**exchange_request.dict())

    session.add(genre_db)
    session.commit()
    session.refresh(genre_db)
    return genre_db


@exchange_request_router.patch("/exchange_request_post{exchange_requests_id}", response_model=ExchangeRequestResponse)
def exchange_requests_post(exchange_request_id: int, update_status: ExchangeRequestUpdateStatus,
                           session=Depends(get_session)):
    db_exchange_request = session.get(ExchangeRequest, exchange_request_id)
    if not db_exchange_request:
        raise HTTPException(status_code=404, detail="Book not found")

    update_data = update_status.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_exchange_request, key, value)

    session.commit()
    session.refresh(db_exchange_request)
    return db_exchange_request


@exchange_request_router.get("/exchange_requests_get", response_model=List[ExchangeRequestResponse])
def exchange_requests_get(session=Depends(get_session)):
    exchange_requests = session.exec(select(ExchangeRequest)).all()

    if not exchange_requests:
        raise HTTPException(status_code=404, detail="Exchange requests not found")
    return exchange_requests


@exchange_request_router.get("/exchange_request_get{exchange_request_id}", response_model=ExchangeRequestResponse)
def exchange_request_get(exchange_request_id: int, session=Depends(get_session)):
    exchange_request = session.get(ExchangeRequest, exchange_request_id)
    if not exchange_request:
        raise HTTPException(status_code=404, detail="Exchange request not found")
    return exchange_request


@exchange_request_router.delete("/exchange_request_delete{exchange_request_id}")
def exchange_request_delete(exchange_request_id: int, session=Depends(get_session)):
    db_exchange_request = session.get(ExchangeRequest, exchange_request_id)
    if not db_exchange_request:
        raise HTTPException(status_code=404, detail="Exchange request not found")
    session.delete(db_exchange_request)
    session.commit()
    return {"ok": True}
