from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from typing import List, Optional
from datetime import date
from connection import get_session
from models.trip_model import Trip, TripCreate, TripUpdate, TripWithFullDetails
from models.user_model import User
from util.auth import get_current_user

router = APIRouter(prefix="/trips", tags=["trips"])


@router.post("/", response_model=Trip)
def create_trip(
        trip: TripCreate,
        current_user: User = Depends(get_current_user),
        session=Depends(get_session)
):
    new_trip = Trip(**trip.dict(), creator_id=current_user.id)
    session.add(new_trip)
    session.commit()
    session.refresh(new_trip)
    return new_trip


@router.get("/", response_model=List[Trip])
def list_trips(
        departure: Optional[str] = Query(None),
        destination: Optional[str] = Query(None),
        start_date: Optional[date] = Query(None),
        end_date: Optional[date] = Query(None),
        session=Depends(get_session)
):
    query = select(Trip)
    if departure:
        query = query.where(Trip.departure == departure)
    if destination:
        query = query.where(Trip.destination == destination)
    if start_date:
        query = query.where(Trip.start_date >= start_date)
    if end_date:
        query = query.where(Trip.end_date <= end_date)
    trips = session.exec(query).all()
    return trips


@router.get("/{trip_id}", response_model=TripWithFullDetails)
def get_trip(trip_id: int, session=Depends(get_session)) -> Trip:
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@router.patch("/{trip_id}", response_model=Trip)
def update_trip(
        trip_id: int,
        trip_update: TripUpdate,
        current_user: User = Depends(get_current_user),
        session=Depends(get_session)
):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if trip.creator_id != current_user.id:
        raise HTTPException(status_code=401, detail="Not authorized to update this trip")
    trip_data = trip_update.dict(exclude_unset=True)
    for key, value in trip_data.items():
        setattr(trip, key, value)
    session.add(trip)
    session.commit()
    session.refresh(trip)
    return trip


@router.delete("/{trip_id}")
def delete_trip(
        trip_id: int,
        current_user: User = Depends(get_current_user),
        session=Depends(get_session)
):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if trip.creator_id != current_user.id:
        raise HTTPException(status_code=401, detail="Not authorized to delete this trip")
    session.delete(trip)
    session.commit()
    return {"msg": "Trip deleted successfully"}


@router.post("/{trip_id}/join")
def join_trip(
        trip_id: int,
        current_user: User = Depends(get_current_user),
        session=Depends(get_session)
):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if current_user in trip.participants:
        raise HTTPException(status_code=400, detail="Already joined this trip")
    trip.participants.append(current_user)
    session.add(trip)
    session.commit()
    session.refresh(trip)
    return {"msg": "Successfully joined the trip", "trip": trip}


@router.delete("/{trip_id}/leave")
def leave_trip(
        trip_id: int,
        current_user: User = Depends(get_current_user),
        session=Depends(get_session)
):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if current_user not in trip.participants:
        raise HTTPException(status_code=400, detail="You are not a participant of this trip")

    trip.participants.remove(current_user)
    session.add(trip)
    session.commit()
    session.refresh(trip)
    return {"msg": "You have successfully left the trip", "trip": trip}
