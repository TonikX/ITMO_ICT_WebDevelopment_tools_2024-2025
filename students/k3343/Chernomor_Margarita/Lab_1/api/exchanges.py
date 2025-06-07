from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import select
from typing import List
from datetime import datetime
from models import ExchangeRequest, ExchangeRequestCreate, ExchangeRequestRead, Library, User, ExchangeStatus
from connection import get_session
from auth.dependencies import get_current_user

router = APIRouter(prefix="/exchanges", tags=["Exchanges"])


@router.post("/exchange", response_model=ExchangeRequestRead)
def create_exchange(
    req: ExchangeRequestCreate,
    session=Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    status = session.exec(
        select(ExchangeStatus).where(ExchangeStatus.name == req.status_name)
    ).first()
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")

    library = session.get(Library, req.library_id)
    if not library or library.user_id != req.to_user_id:
        raise HTTPException(status_code=400, detail="Invalid library or owner")

    new_req = ExchangeRequest(
        from_user_id=current_user.id,
        to_user_id=req.to_user_id,
        library_id=req.library_id,
        status_id=status.id,
        request_date=datetime.utcnow()
    )
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
def update_exchange_status(
    req_id: int,
    status_name: str = Body(embed=True),
    session=Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    req = session.get(ExchangeRequest, req_id)
    if not req:
        raise HTTPException(status_code=404, detail="Exchange not found")

    if req.to_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this exchange")

    status = session.exec(
        select(ExchangeStatus).where(ExchangeStatus.name == status_name)
    ).first()
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")

    req.status_id = status.id

    if status.name == "Accepted":
        req.exchange_date = datetime.utcnow()

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
    return session.exec(select(ExchangeRequest).where(ExchangeRequest.from_user_id == user_id)).all()


@router.get("/user/{user_id}/received")
def get_received_requests(user_id: int, session=Depends(get_session)):
    return session.exec(select(ExchangeRequest).where(ExchangeRequest.to_user_id == user_id)).all()
