# Exchange
```python
class ExchangeDefault(SQLModel):
    offer_id: Optional[int] = Field(default=None, foreign_key="offer.id")

class Exchange(ExchangeDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    offer_id: Optional[int] = Field(default=None, foreign_key="offer.id")
    exchange_date: Optional[str] = None
    offer: Optional[Offer] = Relationship(back_populates="exchange")

```
