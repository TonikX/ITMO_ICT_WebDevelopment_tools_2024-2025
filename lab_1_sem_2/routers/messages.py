from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from db import get_session
from models import *

router = APIRouter()


@router.post("/", response_model=MessageRead)
def send_message(message: MessageCreate, session: Session = Depends(get_session)):
    sender = session.get(User, message.sender_id)
    receiver = session.get(User, message.receiver_id)

    if not sender or not receiver:
        raise HTTPException(status_code=400, detail="Invalid sender or receiver ID")

    db_message = Message(**message.dict())
    session.add(db_message)
    session.commit()
    session.refresh(db_message)

    return db_message


@router.get("/{user_id}", response_model=List[MessageCreate])
def get_user_messages(user_id: int, session: Session = Depends(get_session)):
    messages = session.exec(
        select(Message)
        .options(selectinload(Message.sender), selectinload(Message.receiver))
        .where(Message.receiver_id == user_id)
    ).all()

    if not messages:
        raise HTTPException(status_code=404, detail="No messages found")

    return messages


@router.delete("/{message_id}")
def delete_message(message_id: int, session: Session = Depends(get_session)):
    message = session.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    session.delete(message)
    session.commit()
    return {"status": 200, "message": "Message deleted"}


@router.patch("/{message_id}", response_model=MessageCreate)
def update_message(message_id: int, message_update: MessageUpdate, session: Session = Depends(get_session)):
    db_message = session.get(Message, message_id)
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")

    update_data = message_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_message, key, value)

    session.commit()
    session.refresh(db_message)
    return MessageCreate(**db_message.dict())


