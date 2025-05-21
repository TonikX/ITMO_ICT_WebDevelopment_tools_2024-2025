# Таблица длдя профилей

```python
class Account:
    id: int = Field(default=None, primary_key=True)

    login: str = Field(unique=True)
    password: str
    email: str = Field(unique=True)

    profile: Optional["Profile"] = Relationship(back_populates="account",  sa_relationship_kwargs={"cascade": "all, delete"})

    books: Optional[list["Book"]] = Relationship(back_populates="owner")
    sent_exchanges: Optional[list["Exchange"]] = Relationship(
        back_populates="sender",
        sa_relationship_kwargs={"foreign_keys": "Exchange.sender_id", "cascade": "all, delete"}
    )
    received_exchanges: Optional[list["Exchange"]] = Relationship(
        back_populates="receiver",
        sa_relationship_kwargs={"foreign_keys": "Exchange.receiver_id", "cascade": "all, delete"}
    )
```