# Таблица для обменов

```python
class Exchange:
    id: int = Field(default=None, primary_key=True)

    date: datetime = Field(default_factory=datetime.now)
    status: ExchangeStatusType = Field(default=ExchangeStatusType.pending)
    
    sender_id: int = Field(foreign_key="account.id", ondelete="CASCADE")
    receiver_id: int = Field(foreign_key="account.id", ondelete="CASCADE")
    
    sender: "Account" = Relationship(
        back_populates="sent_exchanges",
        sa_relationship_kwargs={"foreign_keys": "Exchange.sender_id"}
    )
    receiver: "Account" = Relationship(
        back_populates="received_exchanges",
        sa_relationship_kwargs={"foreign_keys": "Exchange.receiver_id"}
    )

    items: Optional[list["Book"]] = Relationship(back_populates="exchange_items", link_model=ExchangeItem, sa_relationship_kwargs={"cascade": "all, delete"})
```