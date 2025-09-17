from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.api.controllers.offer_controller import (
    create_offer, get_offers, get_offer, update_offer, delete_offer
)
from pg.schemas.schema import OfferCreate, OfferRead
from database import get_session

router = APIRouter(prefix="/offers", tags=["offers"])


@router.post("/", response_model=OfferRead)
def api_create_offer(offer_in: OfferCreate, session: Session = Depends(get_session)):
    return create_offer(session, offer_in)


@router.get("/", response_model=List[OfferRead])
def api_get_offers(session: Session = Depends(get_session)):
    return get_offers(session)


@router.get("/{offer_id}", response_model=OfferRead)
def api_get_offer(offer_id: int, session: Session = Depends(get_session)):
    return get_offer(session, offer_id)


@router.put("/{offer_id}", response_model=OfferRead)
def api_update_offer(offer_id: int, offer_in: OfferCreate, session: Session = Depends(get_session)):
    return update_offer(session, offer_id, offer_in)


@router.delete("/{offer_id}")
def api_delete_offer(offer_id: int, session: Session = Depends(get_session)):
    return delete_offer(session, offer_id)
