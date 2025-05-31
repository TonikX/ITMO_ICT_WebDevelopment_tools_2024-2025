from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session
from db.connection import get_session
from auth.utils import auth_scheme
from middleware.user import get_initiator_permission
from services.itineraries_service import (
    get_itineraries,
    add_itinerary,
    delete_itinerary,
)
from models.models import Itinerary

router = APIRouter(tags=["Itineraries"], prefix="/itineraries")


@router.get("/{trip_id}")
async def read_itineraries(
    trip_id: int,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> list[Itinerary]:
    itineraries = get_itineraries(session, trip_id)
    return itineraries


@router.post("/")
async def create_new_itinerary(
    itinerary: Itinerary,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> Itinerary:
    get_initiator_permission(itinerary.trip_id, token=token, session=session)
    new_itinerary = add_itinerary(session, itinerary)
    return new_itinerary


@router.delete("/{trip_id}/{itinerary_id}")
async def remove_itinerary(
    trip_id: int,
    itinerary_id: int,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> bool:
    get_initiator_permission(trip_id, token=token, session=session)
    deleted = delete_itinerary(session, trip_id, itinerary_id)
    return deleted
