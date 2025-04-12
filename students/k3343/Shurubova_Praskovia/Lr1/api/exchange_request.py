from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
from sqlmodel import Session, select
from db import get_session
from models import ExchangeRequest, ExchangeRequestCreate, ExchangeRequestUpdate
from utils.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ExchangeRequest])
def get_requests(request: Request, session: Session = Depends(get_session)):
    get_current_user(request)
    return session.exec(select(ExchangeRequest)).all()


@router.get("/{request_id}", response_model=ExchangeRequest)
def get_request(request: Request, request_id: int, session: Session = Depends(get_session)):
    get_current_user(request)
    req = session.get(ExchangeRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Exchange request not found")
    return req


@router.post("/create", response_model=ExchangeRequest)
def create_request(request: Request, form: ExchangeRequestCreate, session: Session = Depends(get_session)):
    get_current_user(request)
    db_req = ExchangeRequest.model_validate(form)
    session.add(db_req)
    session.commit()
    session.refresh(db_req)
    return db_req


@router.patch("/update/{request_id}", response_model=ExchangeRequest)
def update_request(request: Request, request_id: int, form: ExchangeRequestUpdate, session: Session = Depends(get_session)):
    get_current_user(request)
    db_req = session.get(ExchangeRequest, request_id)
    if not db_req:
        raise HTTPException(status_code=404, detail="Exchange request not found")
    req_data = form.model_dump(exclude_unset=True)
    for key, value in req_data.items():
        setattr(db_req, key, value)
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
