import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from middleware.user import get_initiator_permission
from sqlmodel import Session
from auth.utils import auth_scheme, decode_access_token

from db.connection import get_session
from services.trips_service import (
    get_trip_with_companions,
    create_trip,
    get_trips_with_companions,
    update_trip,
    delete_trip,
)
from models.models import Trip, TripWithCompanions

router = APIRouter(tags=["Trips"], prefix="/trips")


@router.get("/", response_model=list[TripWithCompanions])
async def list_trips(
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    return get_trips_with_companions(session)


@router.get("/{trip_id}", response_model=TripWithCompanions)
async def get_trip_by_id(
    trip_id: int,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    trip = get_trip_with_companions(session, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@router.post("/new", response_model=Trip)
async def create_new_trip(
    trip: Trip,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    user_id_credentials = decode_access_token(token.credentials)
    trip.initiator_id = user_id_credentials.get("user_id")
    trip.created_at = trip.updated_at = datetime.now()
    return create_trip(session, trip)


@router.put("/{trip_id}", response_model=Trip)
async def update_existing_trip(
    trip_id: int,
    trip: Trip,
    session: Session = Depends(get_session),
    _: None = Depends(get_initiator_permission),
):
    updated = update_trip(session, trip_id, trip)
    if not updated:
        raise HTTPException(status_code=404, detail="Trip not found")
    return updated


@router.delete("/{trip_id}")
async def delete_existing_trip(
    trip_id: int,
    session: Session = Depends(get_session),
    _: None = Depends(get_initiator_permission),
):
    deleted = delete_trip(session, trip_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"message": "Trip deleted successfully"}
