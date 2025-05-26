from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from Lr1.connection import get_session
from Lr1.models import (
    ExchangeRequestCreate,
    ExchangeRequest,
    StatusExchangeRequest,
    Library,
    User,
    ExchangeRequestRead
)
from Lr1.core.dependencies import get_current_user

router = APIRouter(prefix="/exchanges", tags=["Exchange Requests"])


@router.post("/", response_model=ExchangeRequestRead, status_code=status.HTTP_201_CREATED)
def create_exchange_request(
        request: ExchangeRequestCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    # Проверка наличия книги у владельца
    owner_entry = session.get(Library, (request.owner_id, request.requested_book_id))
    if not owner_entry or not owner_entry.is_available:
        raise HTTPException(status_code=404, detail="Requested book is not available")

    # Проверка, что текущий пользователь владеет предложенной книгой
    offered_entry = session.get(Library, (current_user.id, request.offered_book_id))
    if not offered_entry or not offered_entry.is_available:
        raise HTTPException(status_code=400, detail="You do not own the offered book")

    existing_request = session.exec(
        select(ExchangeRequest).where(
            ExchangeRequest.requester_id == current_user.id,
            ExchangeRequest.owner_id == request.owner_id,
            ExchangeRequest.requested_book_id == request.requested_book_id,
            ExchangeRequest.offered_book_id == request.offered_book_id,
            ExchangeRequest.status == StatusExchangeRequest.pending
        )
    ).first()
    if existing_request:
        raise HTTPException(status_code=400, detail="This exchange request already exists.")

    exchange = ExchangeRequest(
        requester_id=current_user.id,
        owner_id=request.owner_id,
        requested_book_id=request.requested_book_id,
        offered_book_id=request.offered_book_id
    )
    session.add(exchange)
    session.commit()
    session.refresh(exchange)
    return exchange


@router.get("/me/sent", response_model=list[ExchangeRequestRead])
def get_sent_requests(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    requests = session.exec(
        select(ExchangeRequest).where(ExchangeRequest.requester_id == current_user.id)
    ).all()
    return requests


@router.get("/me/received", response_model=list[ExchangeRequestRead])
def get_received_requests(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    requests = session.exec(
        select(ExchangeRequest).where(ExchangeRequest.owner_id == current_user.id)
    ).all()
    return requests


@router.post("/{request_id}/respond", response_model=ExchangeRequestRead)
def respond_to_exchange_request(
        request_id: int,
        decision: StatusExchangeRequest,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    request = session.get(ExchangeRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Exchange request not found")

    if request.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not the owner of the requested book")

    if request.status != StatusExchangeRequest.pending:
        raise HTTPException(status_code=400, detail="Request has already been processed")

    request.status = decision

    if decision == StatusExchangeRequest.accepted:
        requested_entry = session.get(Library, (request.owner_id, request.requested_book_id))
        offered_entry = session.get(Library, (request.requester_id, request.offered_book_id))

        if not requested_entry or not offered_entry:
            raise HTTPException(status_code=400, detail="One of the books is not available in users' libraries")

        # Меняем владельцев книг
        requested_entry.user_id = request.requester_id
        offered_entry.user_id = request.owner_id

        # Обязательно обновляем, чтобы SQLModel отследил изменения
        session.add(requested_entry)
        session.add(offered_entry)

    session.add(request)
    session.commit()
    session.refresh(request)
    return request


@router.delete("/{request_id}", status_code=204)
def delete_exchange_request(
        request_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    request = session.get(ExchangeRequest, request_id)

    if not request:
        raise HTTPException(status_code=404, detail="Exchange request not found")

    if request.requester_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own requests")

    if request.status != StatusExchangeRequest.pending:
        raise HTTPException(status_code=400, detail="Only pending requests can be deleted")

    session.delete(request)
    session.commit()
    return {"ok": True}
