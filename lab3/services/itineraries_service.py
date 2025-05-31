from datetime import datetime
from sqlmodel import Session, select
from models.models import Itinerary


def get_itineraries(session: Session, trip_id: int) -> list[Itinerary]:
    statement = select(Itinerary).where(Itinerary.trip_id == trip_id)
    itineraries = session.exec(statement).all()
    return itineraries


def add_itinerary(session: Session, itinerary: Itinerary) -> Itinerary:
    itinerary.created_at = datetime.now()
    session.add(itinerary)
    session.commit()
    session.refresh(itinerary)
    return itinerary


def delete_itinerary(session: Session, trip_id: int, itinerary_id: int) -> bool:
    statement = select(Itinerary).where(Itinerary.id == itinerary_id, Itinerary.trip_id == trip_id)
    itinerary = session.exec(statement).one_or_none()
    if itinerary:
        session.delete(itinerary)
        session.commit()
        return True
    return False
