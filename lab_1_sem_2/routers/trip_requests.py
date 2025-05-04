from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from db import get_session
from models import *

router = APIRouter()


@router.get("/", response_model=List[TripRequestRead])
def get_all_trip_requests(session: Session = Depends(get_session)):
    trip_requests = session.query(TripRequest).all()
    return trip_requests


@router.get("/by_trip/{trip_id}", response_model=List[TripRequestRead])
def get_trip_requests_for_trip(trip_id: int, session: Session = Depends(get_session)):
    trip_requests = session.query(TripRequest).filter(TripRequest.trip_id == trip_id).all()
    if not trip_requests:
        raise HTTPException(status_code=404, detail="No trip requests found for this trip")
    return trip_requests


@router.post("/", response_model=TripRequestRead)
def create_trip_request(request: TripRequestCreate, session: Session = Depends(get_session)):
    db_request = TripRequest(**request.dict())
    session.add(db_request)
    session.commit()
    session.refresh(db_request)
    return db_request


@router.get("/{request_id}", response_model=TripRequestRead)
def get_trip_request(request_id: int, session: Session = Depends(get_session)):
    request = session.get(TripRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Trip request not found")
    return request


@router.patch("/{request_id}", response_model=TripRequestRead)
def update_trip_request_status(
        request_id: int,
        status: TripRequestStatus,
        session: Session = Depends(get_session)
):
    db_request = session.get(TripRequest, request_id)
    if not db_request:
        raise HTTPException(status_code=404, detail="Trip request not found")

    db_request.status = status
    session.commit()
    session.refresh(db_request)
    return db_request


@router.delete("/{request_id}", response_model=dict)
def delete_trip_request(request_id: int, session: Session = Depends(get_session)):
    trip_request = session.get(TripRequest, request_id)
    if not trip_request:
        raise HTTPException(status_code=404, detail="Trip request not found")

    session.delete(trip_request)
    session.commit()
    return {"status": 200, "message": "Trip request deleted"}
