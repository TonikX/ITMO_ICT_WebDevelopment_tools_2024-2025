from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session, select
from db.connection import get_session
from auth.utils import decode_access_token, auth_scheme
from services.trips_service import get_trips_by_user
from models.models import Account, Companion


def get_general_access_scope(
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    session: Session = Depends(get_session),
) -> Account:
    payload = decode_access_token(token.credentials)
    if "error" in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    if payload.get("scope") != "user" or payload.get("scope") != "admin":
        raise HTTPException(status_code=403, detail="You have no access to this resource")
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token claims")

    statement = select(Account).where(Account.id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_user_permission(
    user_id: int,
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> None:
    payload = decode_access_token(token.credentials)
    if "error" in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    current_user_id = payload.get("user_id")
    role = payload.get("role")
    if role != "admin" and current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")


def get_user_permission_by_trip(
    user_id: int,
    trip_id: int,
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> None:
    payload = decode_access_token(token.credentials)
    if "error" in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    trips = get_trips_by_user(user_id=user_id)
    for trip in trips:
        if trip.id == trip_id:
            return
    raise HTTPException(status_code=403, detail="Not enough permissions")


def get_initiator_permission(
    trip_id: int,
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    session: Session = Depends(get_session),
) -> None:
    payload = decode_access_token(token.credentials)
    if "error" in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("user_id")
    role = payload.get("role")
    if role == "admin":
        return
    trips = get_trips_by_user(session, user_id)
    for trip in trips:
        if trip.id == trip_id:
            return
    raise HTTPException(status_code=403, detail="Not enough permissions")


def get_message_permission(
    trip_id: int,
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    session: Session = Depends(get_session),
) -> None:
    payload = decode_access_token(token.credentials)
    if "error" in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("user_id")
    role = payload.get("role")
    if role == "admin":
        return
    trips = get_trips_by_user(session, user_id)
    for trip in trips:
        if trip.id == trip_id:
            return
    statement = select(Companion).where(Companion.trip_id == trip_id, Companion.companion_id == user_id)
    companion = session.exec(statement).first()
    if companion:
        return
    raise HTTPException(status_code=403, detail="Not enough permissions")
