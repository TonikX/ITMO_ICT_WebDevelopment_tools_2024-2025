from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload

from db import get_session
from models.exchange import Exchange as ExchangeModel
from schemas.exchange import Exchange as ExchangeSchema, ExchangeCreate, ExchangeUpdate

router = APIRouter()


@router.post("/exchanges/", response_model=ExchangeSchema)
def create_exchange(
        exchange: ExchangeCreate, session: Session = Depends(get_session)
) -> ExchangeSchema:
    db_exchange = ExchangeModel(**exchange.dict())
    session.add(db_exchange)
    session.commit()
    session.refresh(db_exchange)
    return ExchangeSchema.from_orm(db_exchange)


@router.get("/exchanges/{exchange_id}", response_model=ExchangeSchema)
def read_exchange(
        exchange_id: int, session: Session = Depends(get_session)
) -> ExchangeSchema:
    db_exchange = session.query(ExchangeModel).options(
        joinedload(ExchangeModel.owner),
        joinedload(ExchangeModel.requester),
        joinedload(ExchangeModel.owner_book),
        joinedload(ExchangeModel.requester_book)
    ).filter(ExchangeModel.id == exchange_id).first()

    if not db_exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
    return ExchangeSchema.from_orm(db_exchange)


@router.get("/exchanges/", response_model=List[ExchangeSchema])
def read_exchanges(
        skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
) -> List[ExchangeSchema]:
    db_exchanges = session.query(ExchangeModel).offset(skip).limit(limit).all()
    return [ExchangeSchema.from_orm(ex) for ex in db_exchanges]


@router.patch("/exchanges/{exchange_id}", response_model=ExchangeSchema)
def update_exchange(
        exchange_id: int, exchange: ExchangeUpdate, session: Session = Depends(get_session)
) -> ExchangeSchema:
    db_exchange = session.get(ExchangeModel, exchange_id)
    if not db_exchange:
        raise HTTPException(status_code=404, detail="ExchangeSchema not found")

    for key, value in exchange.dict(exclude_unset=True).items():
        setattr(db_exchange, key, value)

    session.add(db_exchange)
    session.commit()
    session.refresh(db_exchange)
    return ExchangeSchema.from_orm(db_exchange)


@router.delete("/exchanges/{exchange_id}", response_model=ExchangeSchema)
def delete_exchange(
        exchange_id: int, session: Session = Depends(get_session)
) -> ExchangeSchema:
    db_exchange = session.get(ExchangeModel, exchange_id)
    if not db_exchange:
        raise HTTPException(status_code=404, detail="ExchangeSchema not found")
    response: ExchangeSchema = ExchangeSchema.from_orm(db_exchange)
    session.delete(db_exchange)
    session.commit()
    return response
