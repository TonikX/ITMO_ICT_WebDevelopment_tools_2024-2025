from fastapi import Depends, HTTPException
from sqlmodel import Session
from app.models.models import Offer, Ownership
from app.api.dependencies.auth import get_current_user
from app.db.session import get_session

def get_current_offer(
    offer_id: int,
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Проверяет, что оффер принадлежит пользователю и является открытым."""
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    ownership = session.get(Ownership, offer.ownership_id)
    if ownership.user_id != user_id:
        raise HTTPException(status_code=403, detail="You can only manage your own offers")

    if not offer.is_open:
        raise HTTPException(status_code=400, detail="Offer is already closed")

    return offer
