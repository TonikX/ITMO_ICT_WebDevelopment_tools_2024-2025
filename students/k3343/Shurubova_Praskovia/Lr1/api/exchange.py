from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
from sqlmodel import Session, select
from db import get_session
from models import Exchange, ExchangeCreate, ExchangeUpdate
from utils.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[Exchange])
def get_exchanges(request: Request, session: Session = Depends(get_session)):
    get_current_user(request)
    return session.exec(select(Exchange)).all()


@router.get("/{exchange_id}", response_model=Exchange)
def get_exchange(request: Request, exchange_id: int, session: Session = Depends(get_session)):
    get_current_user(request)
    exchange = session.get(Exchange, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
    return exchange


@router.post("/create", response_model=Exchange)
def create_exchange(request: Request, exchange: ExchangeCreate, session: Session = Depends(get_session)):
    get_current_user(request)
    db_exchange = Exchange.model_validate(exchange)
    session.add(db_exchange)
    session.commit()
    session.refresh(db_exchange)
    return db_exchange


@router.patch("/update/{exchange_id}", response_model=Exchange)
def update_exchange(request: Request, exchange_id: int, exchange: ExchangeUpdate, session: Session = Depends(get_session)):
    get_current_user(request)
    db_exchange = session.get(Exchange, exchange_id)
    if not db_exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
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
    session.delete(exchange)
    session.commit()
    return {"message": "Exchange deleted"}
