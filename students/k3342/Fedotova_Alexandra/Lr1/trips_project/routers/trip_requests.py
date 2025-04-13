from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session, select
from connection import get_session
from models.models import TripRequest

router = APIRouter(prefix="/trip_requests", tags=["Trip Requests"])


@router.get("", response_model=List[TripRequest])
def get_trip_requests(db: Session = Depends(get_session)):
    return db.exec(select(TripRequest)).all()

@router.post("", response_model=TripRequest)
def create_trip_request(trip_request: TripRequest, db: Session = Depends(get_session)):
    db.add(trip_request)
    db.commit()
    db.refresh(trip_request)
    return trip_request

@router.delete("/{request_id}")
def delete_trip_request(request_id: int, db: Session = Depends(get_session)):
    trip_request = db.get(TripRequest, request_id)
    if not trip_request:
        raise HTTPException(status_code=404, detail="Trip request not found")
    db.delete(trip_request)
    db.commit()
    return {"message": "Trip request deleted successfully"}

@router.patch("/{request_id}/status")
def update_trip_request_status(request_id: int, status: str, db: Session = Depends(get_session)):
    if status not in ["pending", "accepted", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    trip_request = db.get(TripRequest, request_id)
    if not trip_request:
        raise HTTPException(status_code=404, detail="Trip request not found")
    trip_request.status = status
    db.add(trip_request)
    db.commit()
    db.refresh(trip_request)
    return trip_request