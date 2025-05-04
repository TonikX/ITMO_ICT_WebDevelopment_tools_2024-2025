from typing import List, Type
from sqlmodel import Session
from fastapi import FastAPI, Depends, HTTPException

from db import get_session
from models import Trip, TripCreate, TripRead, TripWithDetails, UserCreate, UserRead, User

app = FastAPI()


@app.post("/trips/create", response_model=TripRead)
def create_trip(trip: TripCreate, session: Session = Depends(get_session)):
    db_trip = Trip.from_orm(trip)
    session.add(db_trip)
    session.commit()
    session.refresh(db_trip)
    return db_trip


@app.get("/trips/{trip_id}", response_model=TripRead)
def get_trip(trip_id: int, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@app.get("/trips/", response_model=List[TripRead])
def list_trips(session: Session = Depends(get_session)):
    trips = session.query(Trip).all()
    return trips


@app.patch("/trips/{trip_id}", response_model=TripRead)
def update_trip(
        trip_id: int, trip: TripCreate, session: Session = Depends(get_session)) -> Type[Trip]:
    db_trip = session.get(Trip, trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    trip_data = trip.model_dump(exclude_unset=True)
    for key, value in trip_data.items():
        setattr(db_trip, key, value)
    session.add(db_trip)
    session.commit()
    session.refresh(db_trip)

    return db_trip


@app.get("/trips_vlozhenn/{trip_id}", response_model=TripWithDetails)
def get_trip(trip_id: int, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@app.delete("/trip/delete/{trip_id}")
def delete_trip(trip_id: int, session: Session = Depends(get_session)):
    trip = session.query(Trip).filter(Trip.id == trip_id).first()
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    session.delete(trip)
    session.commit()
    return {"status": 200, "message": "Trip deleted"}


@app.put("/trip/update/{trip_id}", response_model=Trip)
def update_trip(trip_id: int, trip: Trip, session: Session = Depends(get_session)):
    existing_trip = session.query(Trip).filter(Trip.id == trip_id).first()
    if existing_trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    for key, value in trip.dict(exclude_unset=True).items():
        setattr(existing_trip, key, value)
    session.commit()
    session.refresh(existing_trip)
    return existing_trip


@app.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = User.from_orm(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
