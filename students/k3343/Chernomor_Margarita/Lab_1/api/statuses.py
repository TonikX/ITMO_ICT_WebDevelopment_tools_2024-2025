from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing import List
from models import ExchangeStatus, ExchangeStatusCreate, ExchangeRequest
from connection import get_session

router = APIRouter(prefix="/statuses", tags=["Statuses"])


@router.post("/status")
def create_status(status_data: ExchangeStatusCreate, session=Depends(get_session)) -> ExchangeStatus:
    status = ExchangeStatus(**status_data.dict())
    session.add(status)
    session.commit()
    session.refresh(status)
    return status


@router.get("/statuses")
def list_statuses(session=Depends(get_session)) -> List[ExchangeStatus]:
    return session.exec(select(ExchangeStatus)).all()


@router.get("/status/{status_id}")
def get_status(status_id: int, session=Depends(get_session)) -> ExchangeStatus:
    status = session.get(ExchangeStatus, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")
    return status


@router.get("/user/{user_id}/exchanges")
def get_user_exchanges_by_status(
        user_id: int,
        status_name: str,
        session=Depends(get_session)
) -> List[ExchangeRequest]:
    status = session.exec(
        select(ExchangeStatus).where(ExchangeStatus.name == status_name)
    ).first()

    if not status:
        raise HTTPException(status_code=404, detail="Status not found")

    exchanges = session.exec(
        select(ExchangeRequest).where(
            (ExchangeRequest.from_user_id == user_id) | (ExchangeRequest.to_user_id == user_id),
            ExchangeRequest.status_id == status.id
        )
    ).all()

    return exchanges


@router.delete("/status/{status_id}")
def delete_status(status_id: int, session=Depends(get_session)):
    status = session.get(ExchangeStatus, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")
    session.delete(status)
    session.commit()
    return {"ok": True}
