from sqlmodel import Session, select
from models.models import Participant


def get_participants(session: Session, journey_id: int) -> list[Participant]:
    statement = select(Participant).where(Participant.journey_id == journey_id)
    return session.exec(statement).all()


def create_participant(session: Session, participant: Participant) -> Participant:
    session.add(participant)
    session.commit()
    session.refresh(participant)
    return participant


def update_participant(session: Session, participant_id: int, participant: Participant) -> Participant | None:
    db_participant = session.exec(select(Participant).where(Participant.id == participant_id)).one_or_none()
    if db_participant:
        for key, value in participant.dict(exclude_unset=True).items():
            setattr(db_participant, key, value)
        session.commit()
        session.refresh(db_participant)
        return db_participant
    return None


def delete_participant(session: Session, participant_id: int) -> Participant | None:
    db_participant = session.exec(select(Participant).where(Participant.id == participant_id)).one_or_none()
    if db_participant:
        session.delete(db_participant)
        session.commit()
        return db_participant
    return None
