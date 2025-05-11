from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing import List

from connection import get_session
from models.message_model import Message, MessageDetails
from models.trip_model import Trip
from models.user_model import User
from util.auth import get_current_user

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("/", response_model=Message)
def create_message(
    trip_id: int,
    content: str,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session)
):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    new_message = Message(trip_id=trip_id, user_id=current_user.id, content=content)
    session.add(new_message)
    session.commit()
    session.refresh(new_message)
    return new_message

@router.get("/trip/{trip_id}", response_model=List[MessageDetails])
def list_messages_for_trip(trip_id: int, session=Depends(get_session)):
    messages = session.exec(select(Message).where(Message.trip_id == trip_id)).all()
    return messages
