from sqlmodel import Session, select
from app.models.models import Deal, SwapRequest, Offer, Ownership

def get_user_deals(user_id: int, session: Session) -> list[Deal]:
    """
    Получает список завершённых сделок (`Deal`), в которых участвовал пользователь.
    """
    statement = (
        select(Deal)
        .join(SwapRequest, Deal.swap_id == SwapRequest.id)
        .join(Offer, (SwapRequest.get_offer_id == Offer.id) | (SwapRequest.give_offer_id == Offer.id))
        .join(Ownership, Offer.ownership_id == Ownership.id)
        .where(Ownership.user_id == user_id)
    )
    deals = session.exec(statement).all()

    return deals
