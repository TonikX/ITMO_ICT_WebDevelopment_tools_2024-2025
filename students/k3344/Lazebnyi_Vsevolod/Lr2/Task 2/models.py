from sqlmodel import SQLModel, Field
from datetime import date

class StockData(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    asset_name: str
    ticker: str
    investing_id: int
    date: date
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int

