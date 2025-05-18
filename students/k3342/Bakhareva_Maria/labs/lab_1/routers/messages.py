from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from db.connection import get_session
from services.messages_service import get_messages, create_message
from models.models import Message
from fastapi.security import HTTPAuthorizationCredentials
from auth.utils import auth_scheme
from middleware.user import get_message_permission

router = APIRouter(tags=["Messages"], prefix="/messages")


@router.get("/{journey_id}", response_model=list[Message])
async def get_journey_messages(
    journey_id: int,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> list[Message]:
    get_message_permission(journey_id, token=token, session=session)
    messages = get_messages(session, journey_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Messages not found")
    return messages


@router.post("/", response_model=Message)
async def create_journey_message(
    message: Message,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> Message:
    get_message_permission(message.journey_id, token=token, session=session)
    created_message = create_message(session, message)
    return created_message
