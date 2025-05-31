from sqlmodel import Session, select
from models.models import Companion


def get_companions(session: Session, trip_id: int) -> list[Companion]:
    statement = select(Companion).where(Companion.trip_id == trip_id)
    companions = session.exec(statement).all()
    return companions


def create_companion(session: Session, companion: Companion) -> Companion | None:
    session.add(companion)
    session.commit()
    session.refresh(companion)
    return companion


def update_companion(session: Session, companion_id: int, companion: Companion) -> Companion | None:
    statement = select(Companion).where(Companion.id == companion_id)
    db_companion = session.exec(statement).one_or_none()
    if db_companion:
        for key, value in companion.dict().items():
            setattr(db_companion, key, value)
        session.commit()
        session.refresh(db_companion)
        return db_companion
    return None


def delete_companion(session: Session, companion_id: int) -> Companion | None:
    statement = select(Companion).where(Companion.id == companion_id)
    db_companion = session.exec(statement).one_or_none()
    if db_companion:
        session.delete(db_companion)
        session.commit()
        return db_companion
    return None
