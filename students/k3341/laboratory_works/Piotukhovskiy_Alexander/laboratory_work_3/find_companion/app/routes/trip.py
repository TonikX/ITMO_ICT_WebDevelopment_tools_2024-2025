import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from db.database import get_session
from db.models import User, Trip, TripParticipation, TripRole, TripStatus
from dependencies.auth import get_current_user
from schemas.trip import TripCreate, TripUpdate, TripParticipationResponse, TripDetailResponse, TripSearchDto
from schemas.user import *

router = APIRouter()


@router.get("/search", response_model=List[TripResponse])
def search_trips(
        search_params: TripSearchDto,
        session: Session = Depends(get_session),
):
    statement = select(Trip)


    if search_params.departure_location:
        statement = statement.where(Trip.departure_location == search_params.departure_location)
    if search_params.arrival_location:
        statement = statement.where(Trip.arrival_location == search_params.arrival_location)

    if search_params.departure_from:
        statement = statement.where(Trip.departure >= search_params.departure_from)
    if search_params.departure_to:
        statement = statement.where(Trip.departure <= search_params.departure_to)

    if search_params.title:
        statement = statement.where(Trip.title.ilike(f"%{search_params.title}%"))

    if search_params.departure:
        statement = statement.where(Trip.departure == search_params.departure)
    if search_params.arrival:
        statement = statement.where(Trip.arrival == search_params.arrival)

    if search_params.creator_id:
        statement = statement.where(Trip.creator_id == search_params.creator_id)

    trips = session.exec(statement).all()
    return trips

@router.post("", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(
        trip_data: TripCreate,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session),
):
    new_trip = Trip(**trip_data.model_dump(), creator_id=current_user.id)
    session.add(new_trip)
    session.commit()
    session.refresh(new_trip)
    return new_trip


@router.get("/{trip_id}", response_model=TripDetailResponse)
def get_trip_details(
        trip_id: str,
        session: Session = Depends(get_session)
):
    trip = session.get(Trip, uuid.UUID(trip_id))
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found.")

    participants = [
        participation.user
        for participation in trip.participations
        if participation.user is not None
    ]

    trip_detail = TripDetailResponse.model_validate({
        "id": trip.id,
        "title": trip.title,
        "description": trip.description,
        "departure": trip.departure,
        "arrival": trip.arrival,
        "departure_location": trip.departure_location,
        "arrival_location": trip.arrival_location,
        "creator": trip.creator,
        "participants": participants,
    })
    return trip_detail


@router.put("/{trip_id}", response_model=TripResponse)
def update_trip(
        trip_id: UUID,
        trip_data: TripUpdate,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session),
):
    existing_trip = session.get(Trip, trip_id)
    if not existing_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if existing_trip.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this trip")

    update_data = trip_data.model_dump()
    for key, value in update_data.items():
        setattr(existing_trip, key, value)

    session.merge(existing_trip)
    session.commit()
    session.refresh(existing_trip)
    return existing_trip


@router.post("/{trip_id}/subscribe",
             response_model=TripParticipationResponse,
             status_code=status.HTTP_201_CREATED)
def subscribe_trip(
        trip_id: UUID,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found.")

    if trip.creator_id == current_user.id:
        raise HTTPException(
            status_code=409, detail="You are a creator."
        )

    statement = select(TripParticipation).where(TripParticipation.trip_id == trip_id, TripParticipation.user_id == current_user.id)
    existing_participation = session.exec(statement).first()
    if existing_participation:
        raise HTTPException(
            status_code=409, detail="You are already subscribed."
        )

    participation = TripParticipation(
        trip_id=trip_id,
        user_id=current_user.id,
        role=TripRole.passenger,
        status=TripStatus.pending
    )
    session.add(participation)
    session.commit()
    session.refresh(participation)
    return participation


@router.delete("/{trip_id}/subscribe", status_code=status.HTTP_204_NO_CONTENT)
def unsubscribe_trip(
        trip_id: UUID,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found.")

    if trip.creator_id == current_user.id:
        raise HTTPException(
            status_code=400, detail="You are a creator."
        )

    statement = select(TripParticipation).where(TripParticipation.trip_id == trip_id, TripParticipation.user_id == current_user.id)
    participation = session.exec(statement).first()
    if not participation:
        raise HTTPException(
            status_code=400, detail="You are not subscribed."
        )

    session.delete(participation)
    session.commit()

    return