from sqlmodel import Session, select
from models.models import Message


def get_messages(session: Session, journey_id: int) -> list[Message]:
    return session.exec(
        select(Message).where(Message.journey_id == journey_id)
    ).all()


def create_message(session: Session, message: Message) -> Message:
    session.add(message)
    session.commit()
    session.refresh(message)
    return message
