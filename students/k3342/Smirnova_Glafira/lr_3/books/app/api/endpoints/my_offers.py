from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.offers import get_current_offer
from app.api.dependencies.ownership import get_current_ownership
from app.db.session import get_session
from app.schemas.info import MessageResponse
from app.schemas.offer import OfferCreate, OfferUpdate, OfferShort, OfferFull
from app.services.offer_service import add_offer, edit_offer, remove_offer, get_user_offers
from app.utils.mapper import map_offer_list
from app.utils.time import format_datetime

router = APIRouter()

@router.post("/", response_model=OfferShort, status_code=201)
def create_offer(
        offer_create: OfferCreate,
        user_id: int = Depends(get_current_user),
        session: Session = Depends(get_session)
) -> OfferShort:
    """Создаёт оффер для книги."""
    ownership = get_current_ownership(offer_create.book_id, user_id, session)
    offer = add_offer(ownership.id, offer_create.comment, session)
    return OfferShort(id=offer.id, book_id=ownership.book_id, comment=offer.comment, created_at=format_datetime(offer.created_at))

@router.patch("/{offer_id}", response_model=OfferShort)
def update_offer(
    offer_update: OfferUpdate,
    offer=Depends(get_current_offer),
    session: Session = Depends(get_session)
)-> OfferShort:
    """Обновляет комментарий оффера."""
    offer = edit_offer(offer, offer_update, session)
    return OfferShort(id=offer.id, book_id=offer.ownership.book_id, comment=offer.comment, created_at=format_datetime(offer.created_at))

@router.delete("/{offer_id}", response_model=MessageResponse)
def delete_offer(
    offer=Depends(get_current_offer),
    session: Session = Depends(get_session)
) -> MessageResponse:
    """Удаляет оффер."""
    remove_offer(offer, session)
    return MessageResponse(message="Offer deleted successfully")


@router.get("/", response_model=list[OfferFull])
def retrieve_my_offers(
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> list[OfferFull]:
    """Возвращает список всех офферов пользователя с полной информацией."""
    offers = get_user_offers(user_id, session)
    return map_offer_list(offers)
