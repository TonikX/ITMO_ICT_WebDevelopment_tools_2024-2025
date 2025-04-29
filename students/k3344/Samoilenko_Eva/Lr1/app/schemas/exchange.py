from sqlmodel import SQLModel, Field
from .profile import ProfileRead
from .exchangeRequest import ExchangeRequestRead


class ExchangeBase(SQLModel):
    exchange_request_id: int = Field(foreign_key="exchangerequest.id")
    completed: bool = Field(default=True)


class ExchangeRead(SQLModel):
    id: int
    exchange_request: ExchangeRequestRead
    completed: bool
    owner: ProfileRead
