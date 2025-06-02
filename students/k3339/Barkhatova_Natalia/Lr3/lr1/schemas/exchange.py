from datetime import datetime
from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel

from enums.change_status import ChangeStatus

if TYPE_CHECKING:
    from schemas.user import UserShort
    from schemas.book import BookShort


class ExchangeBase(BaseModel):
    change_status: ChangeStatus
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ExchangeCreate(ExchangeBase):
    owner_id: int
    requester_id: int
    owner_book_id: int
    requester_book_id: int

    class Config:
        orm_mode = True


class ExchangeUpdate(ExchangeBase):
    change_status: Optional[ChangeStatus] = None
    owner_id: Optional[int] = None
    requester_id: Optional[int] = None
    owner_book_id: Optional[int] = None
    requester_book_id: Optional[int] = None

    class Config:
        orm_mode = True


class Exchange(ExchangeBase):
    id: int
    owner: "UserShort"
    requester: "UserShort"
    owner_book: "BookShort"
    requester_book: "BookShort"

    class Config:
        orm_mode = True
