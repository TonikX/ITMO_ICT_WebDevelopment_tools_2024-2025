from sqlmodel import Session, select
from models.models import Message


def get_messages(session: Session, trip_id: int) -> list[Message]:
    messages = session.exec(select(Message).where(Message.trip_id == trip_id)).all()
    return messages


def create_message(session: Session, message: Message) -> Message:
    session.add(message)
    session.commit()
    session.refresh(message)
    return message
