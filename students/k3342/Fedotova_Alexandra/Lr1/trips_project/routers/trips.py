from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from datetime import datetime
from connection import get_session
from models.models import Trip, User
from schemas import TripWithMessages

router = APIRouter(prefix="/trips", tags=["Trips"])

@router.get("", response_model=List[Trip])
def get_trips(db: Session = Depends(get_session)):
    return db.exec(select(Trip)).all()

@router.post("", response_model=Trip)
def create_trip(trip: Trip, db: Session = Depends(get_session)):
    user = db.get(User, trip.owner_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip

@router.get("/search", response_model=List[Trip])
def search_trips(destination: Optional[str] = None, start_date: Optional[datetime] = None,
                 end_date: Optional[datetime] = None, owner_id: Optional[int] = None,
                 db: Session = Depends(get_session)):
    query = select(Trip)
    if destination:
        query = query.where(Trip.destination.ilike(f"%{destination}%"))
    if start_date:
        query = query.where(Trip.start_date >= start_date)
    if end_date:
        query = query.where(Trip.end_date <= end_date)
    if owner_id:
        query = query.where(Trip.owner_id == owner_id)
    return db.exec(query).all()

@router.get("/{trip_id}", response_model=Trip)
def get_trip(trip_id: int, db: Session = Depends(get_session)):
    trip = db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@router.get("/{trip_id}/with_messages", response_model=TripWithMessages)
def get_trip_with_messages(trip_id: int, db: Session = Depends(get_session)):
    trip = db.exec(select(Trip).where(Trip.id == trip_id).options(selectinload(Trip.messages))).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@router.delete("/{trip_id}")
def delete_trip(trip_id: int, db: Session = Depends(get_session)):
    trip = db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db.delete(trip)
    db.commit()
    return {"message": "Trip deleted successfully"}
