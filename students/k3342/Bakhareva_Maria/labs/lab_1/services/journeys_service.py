from sqlmodel import Session, select
from models.models import Journey, Participant, ParticipantPublic, UserPublic, JourneyWithParticipants, User

def get_participants_by_journey(session: Session, journey_id: int) -> list[Participant]:
    statement = select(Participant).where(Participant.journey_id == journey_id)
    return session.exec(statement).all()

def get_journeys(session: Session) -> list[Journey]:
    statement = select(Journey)
    return session.exec(statement).all()

def get_journey(session: Session, journey_id: int) -> Journey | None:
    statement = select(Journey).where(Journey.id == journey_id)
    return session.exec(statement).one_or_none()

def get_journeys_by_user(session: Session, user_id: int) -> list[Journey]:
    statement = select(Journey).where(Journey.creator_id == user_id)
    return session.exec(statement).all()

# Сериализация

def serialize_participant(participant: Participant) -> ParticipantPublic:
    return ParticipantPublic(
        id=participant.id,
        status=participant.status,
        added_at=participant.added_at,
        user=UserPublic.model_validate(participant.user) if participant.user else None,
    )

def serialize_journey_with_participants(session: Session, journey: Journey) -> JourneyWithParticipants:
    participants = get_participants_by_journey(session, journey.id)
    participants_public = [serialize_participant(p) for p in participants]
    creator = session.exec(select(User).where(User.id == journey.creator_id)).one_or_none()
    creator_public = UserPublic.model_validate(creator) if creator else None
    journey_data = journey.dict()
    journey_data["creator"] = creator_public
    journey_data.pop("creator_id", None)
    return JourneyWithParticipants(**journey_data, participants=participants_public)

def get_journeys_with_participants(session: Session) -> list[JourneyWithParticipants]:
    journeys = get_journeys(session)
    result = []
    for journey in journeys:
        result.append(serialize_journey_with_participants(session, journey))  # Передаем session сюда
    return result

def get_journey_with_participants(session: Session, journey_id: int) -> JourneyWithParticipants | None:
    journey = get_journey(session, journey_id)
    if not journey:
        return None
    return serialize_journey_with_participants(session, journey)  # Передаем session сюда

def create_journey(session: Session, journey: Journey) -> Journey:
    session.add(journey)
    session.commit()
    session.refresh(journey)
    return journey

def update_journey(session: Session, journey_id: int, journey: Journey) -> Journey | None:
    statement = select(Journey).where(Journey.id == journey_id)
    existing_journey = session.exec(statement).one_or_none()
    if existing_journey:
        for key, value in journey.dict(exclude_unset=True).items():
            setattr(existing_journey, key, value)
        session.commit()
        session.refresh(existing_journey)
        return existing_journey
    return None

def delete_journey(session: Session, journey_id: int) -> bool:
    statement = select(Journey).where(Journey.id == journey_id)
    existing_journey = session.exec(statement).one_or_none()
    if existing_journey:
        session.delete(existing_journey)
        session.commit()
        return True
    return False
