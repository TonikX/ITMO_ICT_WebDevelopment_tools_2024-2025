from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

import app.schemas as schemas
import app.crud as crud
from app.database import get_session
from app.routers.auth import authenticate_request

router = APIRouter(
    prefix="/share-requests",
    tags=["share-requests"],
    dependencies=[Depends(authenticate_request)],
)

@router.post("/", response_model=schemas.ShareRequestRead, status_code=status.HTTP_201_CREATED)
def send_request(rq: schemas.ShareRequestCreate, db: Session = Depends(get_session), current=Depends(authenticate_request)):
    return crud.create_share_request(db, rq, sender_id=current.id)

@router.get("/incoming", response_model=List[schemas.ShareRequestRead])
def incoming(db: Session = Depends(get_session), current=Depends(authenticate_request)):
    return crud.get_incoming_requests(db, current.id)

@router.get("/outgoing", response_model=List[schemas.ShareRequestRead])
def outgoing(db: Session = Depends(get_session), current=Depends(authenticate_request)):
    return crud.get_outgoing_requests(db, current.id)

@router.post("/{req_id}/respond", response_model=schemas.ShareRequestRead)
def respond(req_id: int, resp: schemas.ShareRequestRespond, db: Session = Depends(get_session), current=Depends(authenticate_request)):
    req = db.get(crud.ShareRequest, req_id)
    if not req or req.receiver_id != current.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    return crud.respond_request(db, req_id, resp.approve)

@router.delete("/{req_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_request(req_id: int, db: Session = Depends(get_session), current=Depends(authenticate_request)):
    req = db.get(crud.ShareRequest, req_id)
    if not req or req.sender_id != current.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    crud.delete_request(db, req_id)