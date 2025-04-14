# Таблица для предметов обмена

Таблица для связи m2m

```python
class ExchangeItem:
    exchange_id: int = Field(default=None, foreign_key="exchange.id", primary_key=True, ondelete="CASCADE")
    book_id: int = Field(default=None, foreign_key="book.id", primary_key=True, ondelete="CASCADE")
    direction: DirectionType
```