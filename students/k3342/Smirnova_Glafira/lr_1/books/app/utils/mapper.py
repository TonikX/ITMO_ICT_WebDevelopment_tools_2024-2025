from app.models import SwapRequest
from app.models.models import SwapStatus, Offer
from app.schemas.book import BookRead, BookFull
from app.schemas.offer import OfferInSwapList, OfferFull
from app.schemas.swap import SwapInList, SwapFull
from app.utils.time import format_datetime


def map_swap_in_list(swap: SwapRequest) -> SwapInList:
    """Формирует Pydantic-модель `SwapInList` из ORM-модели `SwapRequest`."""

    swap_result = SwapInList(
        id=swap.id,
        offer_to_give=OfferInSwapList(
            id=swap.give_offer.id,
            user_id=swap.give_offer.ownership.user_id,
            book=BookRead.model_validate(swap.give_offer.ownership.book)
        ),
        comment=swap.comment,
        status=swap.status
    )

    if swap_result.status != SwapStatus.outdated:
        swap_result.offer_to_receive = OfferInSwapList(
            id=swap.get_offer.id,
            user_id=swap.get_offer.ownership.user_id,
            book=BookRead.model_validate(swap.get_offer.ownership.book)
        )

    return swap_result

def map_swap_full(swap: SwapRequest) -> SwapFull:
    """Формирует Pydantic-модель `SwapInList` из ORM-модели `SwapRequest`."""

    swap_result = SwapFull(
        id=swap.id,
        offer_to_give=OfferFull(
            id=swap.give_offer.id,
            user_id=swap.give_offer.ownership.user_id,
            book=BookFull.model_validate(swap.give_offer.ownership.book),
            created_at =format_datetime(swap.give_offer.created_at)
        ),
        comment=swap.comment,
        status=swap.status
    )

    if swap_result.status != SwapStatus.outdated:
        swap_result.offer_to_receive = OfferFull(
            id=swap.get_offer.id,
            user_id=swap.get_offer.ownership.user_id,
            book=BookFull.model_validate(swap.get_offer.ownership.book),
            created_at = format_datetime(swap.get_offer.created_at)
        )

    return swap_result

def map_offer_list(offers: list[Offer]) -> list[OfferFull]:
    return [
        OfferFull(
            id=offer.id,
            user_id=offer.ownership.user_id,
            comment=offer.comment,
            book=offer.ownership.book,
            created_at=format_datetime(offer.created_at)
        )
        for offer in offers
    ]


