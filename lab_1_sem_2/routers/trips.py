from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from db import get_session
from models import *

router = APIRouter()


@router.post("/create", response_model=TripRead)
def create_trip(trip: TripCreate, session: Session = Depends(get_session)):
    db_trip = Trip.from_orm(trip)
    session.add(db_trip)
    session.commit()
    session.refresh(db_trip)
    return db_trip


@router.get("/search", response_model=List[TripRead])
def search_rides(
        destination: Optional[str] = Query(None),
        date: Optional[date] = Query(None),
        db: Session = Depends(get_session)
):
    query = select(Trip)
    if destination:
        query = query.where(Trip.destination == destination)
    if date:
        query = query.where(Trip.start_date <= date, Trip.end_date >= date)
    results = db.exec(query).all()
    return results


@router.get("/{trip_id}", response_model=TripWithDetails)
def get_trip(trip_id: int, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@router.get("/", response_model=List[TripRead])
def list_trips(session: Session = Depends(get_session)):
    return session.query(Trip).all()


@router.patch("/{trip_id}", response_model=TripRead)
def update_trip(trip_id: int, trip: TripUpdate, session: Session = Depends(get_session)):
    db_trip = session.get(Trip, trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    trip_data = trip.model_dump(exclude_unset=True)
    for key, value in trip_data.items():
        setattr(db_trip, key, value)
    session.commit()
    session.refresh(db_trip)
    return db_trip


@router.delete("/delete/{trip_id}")
def delete_trip(trip_id: int, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    for request in trip.trip_requests:
        session.delete(request)

    for saved_trip in trip.saved_by_users:
        session.delete(saved_trip)
    session.delete(trip)
    session.commit()

    return {"status": 200, "message": "Trip deleted"}


@router.get("/{trip_id}/trip_requests", response_model=List[TripRequestWithDetails])
def get_trip_requests(trip_id: int, session: Session = Depends(get_session)):
    trip_requests = session.exec(
        select(TripRequest)
        .options(selectinload(TripRequest.trip), selectinload(TripRequest.user))
        .where(TripRequest.trip_id == trip_id)
    ).all()
    if not trip_requests:
        raise HTTPException(status_code=404, detail="No trip requests found")
    return trip_requests


@router.put("/update/{trip_id}", response_model=TripRead)
def update_trip(trip_id: int, trip: TripUpdate, session: Session = Depends(get_session)):
    db_trip = session.get(Trip, trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    for key, value in trip.dict(exclude_unset=True).items():
        setattr(db_trip, key, value)

    session.commit()
    session.refresh(db_trip)

    return db_trip


@router.get("/trips_vlozhenn/{trip_id}", response_model=TripWithDetails)
def get_trip(trip_id: int, session: Session = Depends(get_session)):
    trip = session.exec(
        select(Trip)
        .options(selectinload(Trip.user), selectinload(Trip.organizer))
        .where(Trip.id == trip_id)
    ).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip
