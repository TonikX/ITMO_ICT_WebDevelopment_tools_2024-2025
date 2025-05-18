from fastapi import Depends, HTTPException
from sqlmodel import Session, select
from app.db.session import get_session
from app.api.dependencies.auth import get_current_user
from app.models.models import SwapRequest, SwapStatus, Offer, Ownership


def get_current_swap_from_user(
        swap_id: int,
        user_id: int = Depends(get_current_user),
        session: Session = Depends(get_session)
) -> SwapRequest:
    """Проверяет, что своп-запрос существует и принадлежит пользователю."""

    swap = session.get(SwapRequest, swap_id)
    if not swap:
        raise HTTPException(status_code=404, detail="Swap request not found")

    statement = select(Ownership).join(Offer).where(
        Offer.id == swap.give_offer_id,
        Ownership.user_id == user_id
    )
    ownership = session.exec(statement).first()

    if not ownership:
        raise HTTPException(status_code=403, detail="You did not authorize this swap request")

    return swap

def get_current_swap_to_user(
        swap_id: int,
        user_id: int = Depends(get_current_user),
        session: Session = Depends(get_session)
) -> SwapRequest:
    """Проверяет, что своп-запрос существует и адресован пользователю."""

    swap = session.get(SwapRequest, swap_id)
    if not swap:
        raise HTTPException(status_code=404, detail="Swap request not found")

    statement = select(Ownership).join(Offer).where(
        Offer.id == swap.get_offer_id,
        Ownership.user_id == user_id
    )
    ownership = session.exec(statement).first()

    if not ownership:
        raise HTTPException(status_code=403, detail="You are not the receiver of this swap request")

    return swap
