from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select, delete
from typing import List

from auth.auth import authenticate_request
from models.models import Trip, TripCreate, TripUpdate, Participant, Review, Discussion, TripOut
from db import get_session

router = APIRouter(prefix="/trips", tags=["Trips"], dependencies=[Depends(authenticate_request)])

@router.get("/", response_model=List[Trip])
def get_trips(session: Session = Depends(get_session)):
    return session.exec(select(Trip)).all()

@router.get("/{trip_id}", response_model=Trip)
def get_trip(trip_id: int, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Такой поездки нет")
    return trip

@router.get("/{trip_id}/details", response_model=TripOut)
def get_trip_details(trip_id: int, session: Session = Depends(get_session)):
    trip = session.exec(
        select(Trip)
        .where(Trip.trip_id == trip_id)
        .options(
            selectinload(Trip.participants).selectinload(Participant.user),
            selectinload(Trip.reviews).selectinload(Review.user),
            selectinload(Trip.discussions).selectinload(Discussion.user),
        )
    ).first()

    if not trip:
        raise HTTPException(status_code=404, detail="Такой поездки нет")
    return trip

@router.post("/", response_model=Trip)
def create_trip(trip: TripCreate, session: Session = Depends(get_session)):
    db_trip = Trip(
        user_id=trip.user_id,
        title=trip.title,
        description=trip.description,
        start_date=trip.start_date.replace(tzinfo=None) if trip.start_date.tzinfo else trip.start_date,
        end_date=trip.end_date.replace(tzinfo=None) if trip.end_date.tzinfo else trip.end_date,
        start_place=trip.start_place,
        destination=trip.destination,
        status=trip.status
    )

    session.add(db_trip)
    session.commit()
    session.refresh(db_trip)
    return db_trip

@router.patch("/{trip_id}", response_model=Trip)
def update_trip(
    trip_id: int,
    trip_update: TripUpdate,
    session: Session = Depends(get_session)
):
    db_trip = session.get(Trip, trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Такой поездки не существует")

    update_data = trip_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value not in [None, ""]:
            setattr(db_trip, key, value)

    session.commit()
    session.refresh(db_trip)
    return db_trip

@router.delete("/{trip_id}")
def delete_trip(trip_id: int, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Такой поездки нет")

    session.exec(delete(Participant).where(Participant.trip_id == trip_id))
    session.exec(delete(Review).where(Review.trip_id == trip_id))
    session.exec(delete(Discussion).where(Discussion.trip_id == trip_id))
    session.delete(trip)
    session.commit()

    return {"message": "Всё успешно удалено"}
