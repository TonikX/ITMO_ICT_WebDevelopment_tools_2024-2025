from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from models import *

router = APIRouter()


@router.post("/", response_model=dict)
def save_trip(data: SaveTripRequest, session: Session = Depends(get_session)):
    user_id = data.user_id
    trip_id = data.trip_id

    existing = session.get(SavedTrip, (user_id, trip_id))
    if existing:
        raise HTTPException(status_code=400, detail="Trip already saved")

    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    saved = SavedTrip(user_id=user_id, trip_id=trip_id)
    session.add(saved)
    session.commit()
    return {"message": "Trip saved"}


@router.delete("/", response_model=dict)
def delete_trip(delete_data: SavedTripDelete, session: Session = Depends(get_session)):
    saved = session.get(SavedTrip, (delete_data.user_id, delete_data.trip_id))
    if not saved:
        raise HTTPException(status_code=404, detail="Saved trip not found")

    session.delete(saved)
    session.commit()
    return {"message": "Trip deleted"}


@router.get("/{user_id}", response_model=list)
def get_saved_trips(user_id: int, session: Session = Depends(get_session)):
    results = session.exec(
        select(SavedTrip).where(SavedTrip.user_id == user_id)).all()
    return [s.trip_id for s in results]
