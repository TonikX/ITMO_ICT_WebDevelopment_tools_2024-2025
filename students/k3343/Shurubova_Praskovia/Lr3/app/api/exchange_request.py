from fastapi import APIRouter, HTTPException, Depends
from starlette.requests import Request

from typing import List
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from app.db import get_session
from app.models.models import (
    ExchangeRequest, ExchangeRequestCreate, ExchangeRequestUpdate,
    Book, BookStatus,  ExchangeRequestInfo
)
from app.utils.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ExchangeRequestInfo])
def get_requests(request: Request, session: Session = Depends(get_session)):
    get_current_user(request)
    requests = session.exec(
        select(ExchangeRequest)
        .options(
            selectinload(ExchangeRequest.sender),
            selectinload(ExchangeRequest.receiver),
            selectinload(ExchangeRequest.book)
        )
    ).all()
    return requests


@router.get("/{request_id}", response_model=ExchangeRequestInfo)
def get_request(request: Request, request_id: int, session: Session = Depends(get_session)):
    get_current_user(request)
    req = session.get(ExchangeRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Exchange request not found")
    return req


@router.post("/create", response_model=ExchangeRequestInfo)
def create_request(request: Request, form: ExchangeRequestCreate, session: Session = Depends(get_session)):
    user = get_current_user(request)

    if form.sender_id is None:
        form.sender_id = user.id

    book = session.get(Book, form.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book.status != BookStatus.available:
        raise HTTPException(status_code=400, detail="Book is not available for exchange")

    if form.receiver_id != book.owner_id:
        raise HTTPException(status_code=400, detail="Receiver must be the book owner")

    db_req = ExchangeRequest(
        sender_id=form.sender_id,
        receiver_id=form.receiver_id,
        book_id=form.book_id,
        message=form.message
    )
    session.add(db_req)
    session.commit()
    session.refresh(db_req)

    return db_req


@router.patch("/update/{request_id}", response_model=ExchangeRequestInfo)
def update_request(
    request: Request,
    request_id: int,
    form: ExchangeRequestUpdate,
    session: Session = Depends(get_session)
):
    user = get_current_user(request)
    print(f"User ID from token: {user['id']}")

    db_req = session.get(ExchangeRequest, request_id)
    if not db_req:
        raise HTTPException(status_code=404, detail="Exchange request not found")

    print(f"Receiver ID from DB request: {db_req.receiver_id}")

    if int(user["id"]) != int(db_req.receiver_id):
        raise HTTPException(status_code=403, detail="Only the receiver can update the request")

    update_data = form.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None and value != "":
            setattr(db_req, field, value)

    session.commit()
    session.refresh(db_req)
    return db_req



@router.delete("/delete/{request_id}")
def delete_request(request: Request, request_id: int, session: Session = Depends(get_session)):
    get_current_user(request)
    req = session.get(ExchangeRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Exchange request not found")
    session.delete(req)
    session.commit()
    return {"message": "Exchange request deleted"}
