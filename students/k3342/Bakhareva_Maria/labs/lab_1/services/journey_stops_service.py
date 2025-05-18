from datetime import datetime
from sqlmodel import Session, select
from models.models import JourneyStop


def get_journey_stops(session: Session, journey_id: int) -> list[JourneyStop]:
    statement = select(JourneyStop).where(JourneyStop.journey_id == journey_id)
    return session.exec(statement).all()


def add_journey_stop(session: Session, stop: JourneyStop) -> JourneyStop:
    stop.created_on = datetime.utcnow()
    session.add(stop)
    session.commit()
    session.refresh(stop)
    return stop


def delete_journey_stop(session: Session, journey_id: int, stop_id: int) -> bool:
    statement = select(JourneyStop).where(
        JourneyStop.id == stop_id,
        JourneyStop.journey_id == journey_id,
    )
    stop = session.exec(statement).one_or_none()
    if stop:
        session.delete(stop)
        session.commit()
        return True
    return False
