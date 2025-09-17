from typing import List
from datetime import datetime
from sqlmodel import Session, select
from fastapi import HTTPException

from src.models import Offer
from pg.schemas.schema import OfferCreate, OfferRead


def create_offer(session: Session, offer_in: OfferCreate) -> OfferRead:
    offer = Offer(**offer_in.dict(), created_at=datetime.utcnow().isoformat())
    session.add(offer)
    session.commit()
    session.refresh(offer)
    return OfferRead.from_orm(offer)


def get_offers(session: Session) -> List[OfferRead]:
    offers = session.exec(select(Offer)).all()
    return [OfferRead.from_orm(o) for o in offers]


def get_offer(session: Session, offer_id: int) -> OfferRead:
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return OfferRead.from_orm(offer)


def update_offer(session: Session, offer_id: int, offer_in: OfferCreate) -> OfferRead:
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    for key, value in offer_in.dict().items():
        setattr(offer, key, value)
    session.add(offer)
    session.commit()
    session.refresh(offer)
    return OfferRead.from_orm(offer)


def delete_offer(session: Session, offer_id: int):
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    session.delete(offer)
    session.commit()
    return {"detail": f"Offer {offer_id} deleted"}
