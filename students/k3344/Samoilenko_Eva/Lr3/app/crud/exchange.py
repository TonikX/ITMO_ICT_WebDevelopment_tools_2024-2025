from typing import List

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import selectinload
from ..db.connection import get_session
from sqlmodel import select

from ..models.exchange import Exchange
from ..models.exchangeRequest import ExchangeRequest
from ..schemas.exchange import ExchangeRead

router = APIRouter()


@router.get("/exchanges/{book_id}", response_model=List[ExchangeRead])
def get_exchanges_by_book(book_id: int, session=Depends(get_session)):
    statement = (
        select(Exchange)
        .where(Exchange.book_id == book_id)
        .options(
            selectinload(Exchange.exchange_request)
            .selectinload(ExchangeRequest.requester),
            selectinload(Exchange.exchange_request)
            .selectinload(ExchangeRequest.book),
            selectinload(Exchange.owner)
        )
    )
    results = session.exec(statement).all()

    if not results:
        raise HTTPException(status_code=404, detail="No exchanges found for this book")

    return results
