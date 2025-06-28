from sqlalchemy.orm import Session
from app.models.exchange_request import ExchangeRequest, ExchangeStatus
from app.models.exchange_status_history import ExchangeStatusHistory
from app.schemas.exchange_request import ExchangeRequestCreate
from app.models.user import User
from typing import List, Optional
from datetime import datetime
from app.crud.user_book import get_userbook

def create_exchange_request(db: Session, sender: User, req_in: ExchangeRequestCreate) -> ExchangeRequest:
    # Валидация совпадения названия и автора книги с userbook
    if req_in.sender_book_id:
        sender_userbook = get_userbook(db, req_in.sender_book_id)
        if not sender_userbook:
            raise ValueError("Sender userbook not found")
        if hasattr(req_in, 'book_title') and req_in.book_title is not None:
            if sender_userbook.book.title != req_in.book_title:
                raise ValueError("Sender book title does not match userbook")
        if hasattr(req_in, 'book_author') and req_in.book_author is not None:
            if sender_userbook.book.author != req_in.book_author:
                raise ValueError("Sender book author does not match userbook")
    if req_in.receiver_book_id:
        receiver_userbook = get_userbook(db, req_in.receiver_book_id)
        if not receiver_userbook:
            raise ValueError("Receiver userbook not found")
        if hasattr(req_in, 'book_title') and req_in.book_title is not None:
            if receiver_userbook.book.title != req_in.book_title:
                raise ValueError("Receiver book title does not match userbook")
        if hasattr(req_in, 'book_author') and req_in.book_author is not None:
            if receiver_userbook.book.author != req_in.book_author:
                raise ValueError("Receiver book author does not match userbook")
    req = ExchangeRequest(
        sender_id=sender.id,
        receiver_id=req_in.receiver_id,
        sender_book_id=req_in.sender_book_id,
        receiver_book_id=req_in.receiver_book_id,
        status=ExchangeStatus.pending,
        created_at=datetime.utcnow()
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    # История статусов
    history = ExchangeStatusHistory(
        exchange_request_id=req.id,
        status=ExchangeStatus.pending,
        changed_at=datetime.utcnow()
    )
    db.add(history)
    db.commit()
    return req

def get_exchange_request(db: Session, req_id: int) -> Optional[ExchangeRequest]:
    return db.query(ExchangeRequest).filter(ExchangeRequest.id == req_id).first()

def get_incoming_requests(db: Session, user: User) -> List[ExchangeRequest]:
    return db.query(ExchangeRequest).filter(ExchangeRequest.receiver_id == user.id).all()

def get_outgoing_requests(db: Session, user: User) -> List[ExchangeRequest]:
    return db.query(ExchangeRequest).filter(ExchangeRequest.sender_id == user.id).all()

def update_exchange_status(db: Session, req: ExchangeRequest, new_status: ExchangeStatus) -> ExchangeRequest:
    req.status = new_status
    db.commit()
    db.refresh(req)
    history = ExchangeStatusHistory(
        exchange_request_id=req.id,
        status=new_status,
        changed_at=datetime.utcnow()
    )
    db.add(history)
    db.commit()
    return req

def get_status_history(db: Session, req_id: int) -> List[ExchangeStatusHistory]:
    return db.query(ExchangeStatusHistory).filter(ExchangeStatusHistory.exchange_request_id == req_id).all() 