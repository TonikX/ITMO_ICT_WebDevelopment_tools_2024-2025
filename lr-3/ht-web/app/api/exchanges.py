from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.exchange_request import ExchangeRequestCreate, ExchangeRequestRead, ExchangeStatusHistoryRead, ExchangeStatus
from app.crud.exchange_request import create_exchange_request, get_exchange_request, get_incoming_requests, get_outgoing_requests, update_exchange_status, get_status_history
from app.api.deps import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.exchange_request import ExchangeStatus as ModelExchangeStatus
from typing import List

router = APIRouter()

@router.post("/", response_model=ExchangeRequestRead)
def create_exchange(req_in: ExchangeRequestCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    req = create_exchange_request(db, current_user, req_in)
    return req

@router.get("/incoming", response_model=List[ExchangeRequestRead])
def incoming_exchanges(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_incoming_requests(db, current_user)

@router.get("/outgoing", response_model=List[ExchangeRequestRead])
def outgoing_exchanges(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_outgoing_requests(db, current_user)

@router.patch("/{exchange_id}/status", response_model=ExchangeRequestRead)
def change_status(exchange_id: int, new_status: ExchangeStatus, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    req = get_exchange_request(db, exchange_id)
    if not req:
        raise HTTPException(status_code=404, detail="ExchangeRequest not found")
    # Проверка прав: только участники могут менять статус
    if current_user.id not in [req.sender_id, req.receiver_id]:
        raise HTTPException(status_code=403, detail="Not allowed")
    req = update_exchange_status(db, req, ModelExchangeStatus(new_status))
    return req

@router.get("/{exchange_id}/history", response_model=List[ExchangeStatusHistoryRead])
def status_history(exchange_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    req = get_exchange_request(db, exchange_id)
    if not req:
        raise HTTPException(status_code=404, detail="ExchangeRequest not found")
    if current_user.id not in [req.sender_id, req.receiver_id]:
        raise HTTPException(status_code=403, detail="Not allowed")
    return get_status_history(db, exchange_id) 