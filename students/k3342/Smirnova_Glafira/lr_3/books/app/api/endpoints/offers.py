from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.dependencies.auth import get_current_user
from app.db.session import get_session
from app.schemas.offer import OfferFull, OfferFilter
from app.services.offer_service import get_offer_by_id, filter_offers
from app.utils.mapper import map_offer_list
from app.utils.time import format_datetime

router = APIRouter()

@router.get("/{offer_id}", response_model=OfferFull)
def retrieve_offer(
    offer_id: int,
    _ : int = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> OfferFull:
    """Возвращает один оффер с полной информацией."""
    offer = get_offer_by_id(offer_id, session)
    return OfferFull(
        id=offer.id,
        user_id=offer.ownership.user_id,
        comment=offer.comment,
        book=offer.ownership.book,
        created_at=format_datetime(offer.created_at)
    )

@router.get("/search/", response_model=list[OfferFull])
def search_offers(
    filters: OfferFilter = Depends(),
    _ : int = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> list[OfferFull]:
    """
    Ищет офферы по названию книги, автору, диапазону, жанрам и владельцу.
    Доступна сортировка по дате создания оффера.
    """
    offers = filter_offers(filters, session)
    return map_offer_list(offers)

