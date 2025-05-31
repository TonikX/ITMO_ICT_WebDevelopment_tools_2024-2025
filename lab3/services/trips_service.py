from services.users_service import get_user_by_id
from sqlmodel import Session, select
from models.models import AccountPublic, Companion, CompanionPublic, Trip, TripWithCompanions


def get_companions_by_trip(session: Session, trip_id: int) -> list[Companion]:
    statement = select(Companion).where(Companion.trip_id == trip_id)
    return session.exec(statement).all()


def get_trips(session: Session) -> list[Trip]:
    statement = select(Trip)
    trips = session.exec(statement).all()
    return trips


def get_trip(session: Session, trip_id: int) -> Trip | None:
    statement = select(Trip).where(Trip.id == trip_id)
    trip = session.exec(statement).one_or_none()
    return trip


def serialize_companion(companion: Companion) -> CompanionPublic:
    return CompanionPublic(
        id=companion.id,
        first_name=companion.companion.first_name if companion.companion else "",
        last_name=companion.companion.last_name if companion.companion else "",
        status=companion.status,
        created_at=companion.created_at,
    )


def get_trips_with_companions(session: Session) -> list[TripWithCompanions]:
    trips = get_trips(session)
    result = []
    for trip in trips:
        companions = get_companions_by_trip(session, trip.id)
        companions_public = [serialize_companion(c) for c in companions]
        initiator = get_user_by_id(session, trip.initiator_id)
        initiator_public = AccountPublic.model_validate(initiator) if initiator else None
        trip_data = trip.dict()
        trip_data["initiator"] = initiator_public
        trip_data.pop("initiator_id", None)
        result.append(TripWithCompanions(**trip_data, companions=companions_public))
    return result


def get_trip_with_companions(session: Session, trip_id: int) -> TripWithCompanions | None:
    trip = get_trip(session, trip_id)
    if not trip:
        return None
    companions = get_companions_by_trip(session, trip_id)
    companions_public = [serialize_companion(c) for c in companions]
    initiator = get_user_by_id(session, trip.initiator_id)
    initiator_public = AccountPublic.model_validate(initiator) if initiator else None
    trip_data = trip.dict()
    trip_data["initiator"] = initiator_public
    trip_data.pop("initiator_id", None)
    return TripWithCompanions(**trip_data, companions=companions_public)


def get_trips_by_user(session: Session, user_id: int) -> list[Trip]:
    trips = []
    for trip in session.exec(select(Trip)).all():
        if trip.initiator_id == user_id:
            trips.append(trip)
    return trips


def create_trip(session: Session, trip: Trip) -> Trip:
    session.add(trip)
    session.commit()
    session.refresh(trip)
    return trip


def update_trip(session: Session, trip_id: int, trip: Trip) -> Trip | None:
    statement = select(Trip).where(Trip.id == trip_id)
    existing_trip = session.exec(statement).one_or_none()
    if existing_trip:
        for key, value in trip.dict().items():
            setattr(existing_trip, key, value)
        session.commit()
        session.refresh(existing_trip)
        return existing_trip
    return None


def delete_trip(session: Session, trip_id: int) -> bool:
    statement = select(Trip).where(Trip.id == trip_id)
    existing_trip = session.exec(statement).one_or_none()
    if existing_trip:
        session.delete(existing_trip)
        session.commit()
        return True
    return False
