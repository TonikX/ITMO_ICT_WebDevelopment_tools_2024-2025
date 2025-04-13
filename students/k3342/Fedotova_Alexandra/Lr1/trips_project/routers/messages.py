from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session, select
from connection import get_session
from models.models import Message

router = APIRouter(prefix="/messages", tags=["Messages"])

@router.get("", response_model=List[Message])
def get_messages(db: Session = Depends(get_session)):
    return db.exec(select(Message)).all()

@router.post("", response_model=Message)
def create_message(message: Message, db: Session = Depends(get_session)):
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

@router.delete("/{message_id}")
def delete_message(message_id: int, db: Session = Depends(get_session)):
    message = db.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(message)
    db.commit()
    return {"message": "Message deleted successfully"}