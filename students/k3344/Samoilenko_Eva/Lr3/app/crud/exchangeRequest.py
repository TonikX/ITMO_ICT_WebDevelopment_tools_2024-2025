from fastapi import Depends, HTTPException, APIRouter
from ..db.connection import get_session
from sqlmodel import select

from ..models.book import Book
from ..models.exchange import Exchange
from ..models.exchangeRequest import ExchangeRequest
from ..models.profile import Profile
from ..models.profileLibrary import ProfileLibrary
from ..schemas.exchangeRequest import ExchangeRequestBase, ExchangeRequestRead

router = APIRouter()


@router.post("/exchange-requests/", response_model=ExchangeRequest)
def create_exchange_request(exchange_request: ExchangeRequestBase, session=Depends(get_session)):
    new_exchange_request = ExchangeRequest(**exchange_request.model_dump())

    session.add(new_exchange_request)
    session.commit()
    session.refresh(new_exchange_request)
    return new_exchange_request


@router.get("/exchange-requests/{request_id}", response_model=ExchangeRequestRead)
def get_exchange_request(request_id: int, session=Depends(get_session)):
    exchange_request = session.get(ExchangeRequest, request_id)

    if not exchange_request:
        raise HTTPException(status_code=404, detail="Exchange request not found")

    requester = session.exec(
        select(Profile)
        .where(Profile.id == exchange_request.requester_id)).first()

    requested_book = session.exec(
        select(Book)
        .where(Book.id == exchange_request.requested_book_id)).first()

    return ExchangeRequestRead(id=request_id, status=exchange_request.status, requester=requester,
                               book=requested_book)


@router.patch("/exchange-requests/{request_id}", response_model=ExchangeRequest)
def update_exchange_request_status(request_id: int, status: str,
                                   session=Depends(get_session)):
    exchange_request = session.get(ExchangeRequest, request_id)
    if not exchange_request:
        raise HTTPException(status_code=404, detail="Exchange request not found")

    exchange_request.status = status
    session.add(exchange_request)
    session.commit()
    session.refresh(exchange_request)

    if exchange_request.status == "complete":
        requester = session.get(Profile, exchange_request.requester_id)
        requested_book = session.get(Book, exchange_request.requested_book_id)
        library = session.exec(
            select(ProfileLibrary)
            .where(ProfileLibrary.id == requested_book.profile_library_id)).first()

        if not requester or not requested_book:
            raise HTTPException(status_code=400, detail="Requester or requested book not found")

        new_exchange = Exchange(
            exchange_request_id=exchange_request.id,
            requester_id=exchange_request.requester_id,
            owner_id=library.profile_id,
            book_id=requested_book.id
        )

        session.add(new_exchange)
        session.commit()
        session.refresh(new_exchange)

    return exchange_request
