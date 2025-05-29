# Таблица длдя профилей

```python
class Book:
    id: int = Field(default=None, primary_key=True)

    owner_id: int
    title: str
    author: str|None
    year: int|None
    condition: ConditionType
    genre: str|None
    language: str|None
    description: str|None
    status: BookStatusType = Field(default=BookStatusType.available)

    owner_id: int|None = Field(foreign_key="account.id")

    owner: Optional["Account"] = Relationship(back_populates="books")
    exchange_items: Optional[list["Exchange"]] = Relationship(back_populates="items", link_model=ExchangeItem, sa_relationship_kwargs={"cascade": "all, delete"})
```