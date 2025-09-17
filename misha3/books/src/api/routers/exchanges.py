from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.api.controllers.exchange_controller import (
    create_exchange, get_exchanges, get_exchange, update_exchange, delete_exchange
)
from pg.schemas.schema import ExchangeCreate, ExchangeRead
from database import get_session

router = APIRouter(prefix="/exchanges", tags=["exchanges"])


@router.post("/", response_model=ExchangeRead)
def api_create_exchange(exch_in: ExchangeCreate, session: Session = Depends(get_session)):
    return create_exchange(session, exch_in)


@router.get("/", response_model=List[ExchangeRead])
def api_get_exchanges(session: Session = Depends(get_session)):
    return get_exchanges(session)


@router.get("/{exch_id}", response_model=ExchangeRead)
def api_get_exchange(exch_id: int, session: Session = Depends(get_session)):
    return get_exchange(session, exch_id)


@router.put("/{exch_id}", response_model=ExchangeRead)
def api_update_exchange(exch_id: int, exch_in: ExchangeCreate, session: Session = Depends(get_session)):
    return update_exchange(session, exch_id, exch_in)


@router.delete("/{exch_id}")
def api_delete_exchange(exch_id: int, session: Session = Depends(get_session)):
    return delete_exchange(session, exch_id)
