from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from db.connection import get_session
from services.messages_service import get_messages, create_message
from models.models import Message
from fastapi.security import HTTPAuthorizationCredentials
from auth.utils import auth_scheme, decode_access_token
from middleware.user import get_message_permission

router = APIRouter(tags=["Messages"], prefix="/messages")


@router.get("/{trip_id}")
async def get_trip_messages(
    trip_id: int,
    session: Session = Depends(get_session),
    _: None = Depends(get_message_permission),
) -> list[Message]:
    messages = get_messages(session, trip_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Messages not found")
    return messages


@router.post("/")
async def create_trip_message(
    message: Message,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> Message:
    user_id_credentials = decode_access_token(token.credentials)
    sender_id = user_id_credentials.get("user_id")
    message.sender_id = sender_id
    get_message_permission(message.trip_id, token=token, session=session)
    created_message = create_message(session, message)
    if not created_message:
        raise HTTPException(status_code=400, detail="Error creating message")
    return created_message
