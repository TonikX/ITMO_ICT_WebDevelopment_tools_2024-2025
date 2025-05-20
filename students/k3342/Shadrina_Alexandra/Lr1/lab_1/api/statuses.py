from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing import List
from models import ExchangeStatus
from connection import get_session

router = APIRouter(prefix="/statuses", tags=["Statuses"])


@router.post("/status")
def create_status(status: ExchangeStatus, session=Depends(get_session)) -> ExchangeStatus:
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
