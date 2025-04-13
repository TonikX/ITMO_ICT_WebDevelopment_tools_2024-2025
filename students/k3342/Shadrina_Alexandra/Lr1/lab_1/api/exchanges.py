from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing import List
from datetime import datetime
from models import ExchangeRequest, ExchangeRequestBase, ExchangeRequestRead
from connection import get_session

router = APIRouter(prefix="/exchanges", tags=["Exchanges"])


@router.post("/exchange", response_model=ExchangeRequestRead)
def create_exchange(req: ExchangeRequestBase, session=Depends(get_session)):
    new_req = ExchangeRequest.model_validate(req)
    new_req.request_date = datetime.utcnow()
    session.add(new_req)
    session.commit()
    session.refresh(new_req)
    return new_req


@router.get("/exchange/{req_id}", response_model=ExchangeRequestRead)
def get_exchange(req_id: int, session=Depends(get_session)):
    req = session.get(ExchangeRequest, req_id)
    if not req:
        raise HTTPException(status_code=404, detail="Exchange not found")
    return req


@router.get("/exchanges", response_model=List[ExchangeRequestRead])
def list_exchanges(session=Depends(get_session)):
    return session.exec(select(ExchangeRequest)).all()


@router.patch("/exchange/{req_id}/status")
def update_exchange_status(req_id: int, new_status: str, session=Depends(get_session)):
    req = session.get(ExchangeRequest, req_id)
    if not req:
        raise HTTPException(status_code=404, detail="Exchange not found")
    req.status = new_status
    session.commit()
    session.refresh(req)
    return req


@router.delete("/exchange/{req_id}")
def delete_exchange(req_id: int, session=Depends(get_session)):
    req = session.get(ExchangeRequest, req_id)
    if not req:
        raise HTTPException(status_code=404, detail="Exchange not found")
    session.delete(req)
    session.commit()
    return {"ok": True}


@router.get("/user/{user_id}/sent")
def get_sent_requests(user_id: int, session=Depends(get_session)):
    return session.exec(select(ExchangeRequest).where(ExchangeRequest.sender_id == user_id)).all()


@router.get("/user/{user_id}/received")
def get_received_requests(user_id: int, session=Depends(get_session)):
    return session.exec(select(ExchangeRequest).where(ExchangeRequest.receiver_id == user_id)).all()

