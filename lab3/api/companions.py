from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from middleware.user import get_initiator_permission
from sqlmodel import Session, select

from db.connection import get_session
from auth.utils import auth_scheme
from services.companions_service import (
    get_companions,
    create_companion,
    delete_companion,
    update_companion,
)
from models.models import Companion

router = APIRouter(tags=["Companions"], prefix="/companions")


@router.get("/")
async def read_companions(
    trip_id: int,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> list[Companion]:
    companions = get_companions(session, trip_id)
    return companions


@router.post("/")
async def create_new_companion(
    companion: Companion,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> Companion:
    get_initiator_permission(companion.trip_id, token=token, session=session)
    try:
        new_companion = create_companion(session, companion)
        return new_companion
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{companion_id}")
async def modify_companion(
    companion_id: int,
    companion: Companion,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> Companion:
    statement = select(Companion).where(Companion.id == companion_id)
    db_companion = session.exec(statement).one_or_none()
    if not db_companion:
        raise HTTPException(status_code=404, detail="Companion not found")
    get_initiator_permission(db_companion.trip_id, token=token, session=session)
    try:
        updated_companion = update_companion(session, companion_id, companion)
        if not updated_companion:
            raise HTTPException(status_code=404, detail="Companion not found")
        return updated_companion
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{companion_id}")
async def remove_companion(
    companion_id: int,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> Companion:
    statement = select(Companion).where(Companion.id == companion_id)
    db_companion = session.exec(statement).one_or_none()
    if not db_companion:
        raise HTTPException(status_code=404, detail="Companion not found")
    get_initiator_permission(db_companion.trip_id, token=token, session=session)
    try:
        deleted_companion = delete_companion(session, companion_id)
        if not deleted_companion:
            raise HTTPException(status_code=404, detail="Companion not found")
        return deleted_companion
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
