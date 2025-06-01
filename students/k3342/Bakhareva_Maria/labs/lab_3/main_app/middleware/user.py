from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session, select
from db.connection import get_session
from auth.utils import decode_access_token, auth_scheme
from models.models import User, Journey, Participant
from services.journeys_service import get_journeys_by_user


def get_general_access_scope(
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    session: Session = Depends(get_session),
) -> User:
    payload = decode_access_token(token.credentials)
    if "error" in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    if payload.get("scope") not in ["user", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    user = session.exec(select(User).where(User.id == payload.get("user_id"))).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_user_permission(user_id: int, token: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> None:
    payload = decode_access_token(token.credentials)
    if "error" in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    current_user_id = payload.get("user_id")
    role = payload.get("scope")
    if role != "admin" and current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")


def get_user_permission_by_journey(
    user_id: int,
    journey_id: int,
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    session: Session = Depends(get_session),
) -> None:
    payload = decode_access_token(token.credentials)
    if "error" in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    journeys = get_journeys_by_user(session, user_id)
    if not any(j.id == journey_id for j in journeys):
        raise HTTPException(status_code=403, detail="Not enough permissions")


def get_initiator_permission(
    journey_id: int,
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    session: Session = Depends(get_session),
) -> None:
    payload = decode_access_token(token.credentials)
    if "error" in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("user_id")
    role = payload.get("scope")
    if role == "admin":
        return
    journey = session.exec(select(Journey).where(Journey.id == journey_id)).first()
    if not journey or journey.creator_id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")


def get_message_permission(
    journey_id: int,
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    session: Session = Depends(get_session),
) -> None:
    payload = decode_access_token(token.credentials)
    if "error" in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("user_id")
    role = payload.get("scope")
    if role == "admin":
        return
    statement = select(Participant).where(
        Participant.journey_id == journey_id,
        Participant.user_id == user_id
    )
    participant = session.exec(statement).first()
    if participant:
        return
    raise HTTPException(status_code=403, detail="Not enough permissions")
