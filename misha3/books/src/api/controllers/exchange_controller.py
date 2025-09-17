from typing import List
from datetime import datetime
from sqlmodel import Session, select
from fastapi import HTTPException

from src.models import Exchange
from pg.schemas.schema import ExchangeCreate, ExchangeRead


def create_exchange(session: Session, exch_in: ExchangeCreate) -> ExchangeRead:
    exch = Exchange(**exch_in.dict(), exchange_date=datetime.utcnow().isoformat())
    session.add(exch)
    session.commit()
    session.refresh(exch)
    return ExchangeRead.from_orm(exch)


def get_exchanges(session: Session) -> List[ExchangeRead]:
    exchanges = session.exec(select(Exchange)).all()
    return [ExchangeRead.from_orm(e) for e in exchanges]


def get_exchange(session: Session, exch_id: int) -> ExchangeRead:
    exch = session.get(Exchange, exch_id)
    if not exch:
        raise HTTPException(status_code=404, detail="Exchange not found")
    return ExchangeRead.from_orm(exch)


def update_exchange(session: Session, exch_id: int, exch_in: ExchangeCreate) -> ExchangeRead:
    exch = session.get(Exchange, exch_id)
    if not exch:
        raise HTTPException(status_code=404, detail="Exchange not found")
    for key, value in exch_in.dict().items():
        setattr(exch, key, value)
    exch.exchange_date = datetime.utcnow().isoformat()
    session.add(exch)
    session.commit()
    session.refresh(exch)
    return ExchangeRead.from_orm(exch)


def delete_exchange(session: Session, exch_id: int):
    exch = session.get(Exchange, exch_id)
    if not exch:
        raise HTTPException(status_code=404, detail="Exchange not found")
    session.delete(exch)
    session.commit()
    return {"detail": f"Exchange {exch_id} deleted"}
