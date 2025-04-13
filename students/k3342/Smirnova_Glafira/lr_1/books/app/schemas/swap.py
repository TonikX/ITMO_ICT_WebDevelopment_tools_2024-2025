from sqlmodel import SQLModel

from app.models.models import SwapStatus
from app.schemas.offer import OfferInSwapList, OfferFull


class SwapUpdate(SQLModel):
    comment: str | None = ""

class SwapCreate(SQLModel):
    """Схема для создания запроса на обмен."""
    get_offer_id: int
    give_offer_id: int
    comment: str | None = ""

class SwapRead(SwapCreate):
    """Схема для возврата данных о своп-запросе."""
    id: int
    status: SwapStatus

class SwapInList(SQLModel):
    id: int
    offer_to_give: OfferInSwapList
    offer_to_receive: OfferInSwapList | str = "This offer was closed by the owner"
    comment: str | None = ""
    status: SwapStatus


class SwapFull(SwapInList):
    offer_to_give: OfferFull
    offer_to_receive: OfferFull | str = "This offer was closed by the owner"
