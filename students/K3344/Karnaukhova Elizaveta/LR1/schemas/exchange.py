# from typing import Optional
# from pydantic import BaseModel
# from user import UserProfileRead
# from book import BookItemRead
#
#
# class ExchangeRequestBase(BaseModel):
#     requested_book_id: int
#     offered_book_id: Optional[int] = None
#     status: str = "pending"
#
#
# class ExchangeRequestCreate(ExchangeRequestBase):
#     pass
#
#
# class ExchangeRequestRead(ExchangeRequestBase):
#     id: int
#     requester: UserProfileRead
#     requested_book: BookItemRead
#     offered_book: Optional[BookItemRead] = None
from typing import Optional
from pydantic import BaseModel, Field
from pydantic import BaseModel, ConfigDict

class ExchangeRequestBase(BaseModel):
    requested_book_id: int = Field(..., description="ID запрашиваемой книги")
    offered_book_id: Optional[int] = Field(None, description="ID предлагаемой книги (если есть)")
    status: str = Field("pending", description="Статус запроса на обмен")


class ExchangeRequestCreate(ExchangeRequestBase):
    requester_id: int = Field(..., description="ID пользователя, который отправляет запрос")


class ExchangeRequestRead(ExchangeRequestBase):
    id: int = Field(..., description="ID запроса на обмен")

    class Config:
        from_attributes = True  # Указываем, что можно использовать from_orm


class ExchangeResponse(BaseModel):
    message: str
    exchange_request: ExchangeRequestRead
