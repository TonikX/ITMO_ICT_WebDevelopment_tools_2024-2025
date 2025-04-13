from sqlmodel import SQLModel
from app.schemas.swap import SwapInList

class DealRead(SQLModel):
    """Схема для возврата информации о завершённых обменах (Deal)."""
    id: int
    swap: SwapInList
    date_time: str
