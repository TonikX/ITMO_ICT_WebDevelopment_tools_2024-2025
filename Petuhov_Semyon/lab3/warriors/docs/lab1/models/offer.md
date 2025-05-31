# Offer
```python
class OfferDefault(SQLModel):
    sender_id: Optional[int] = Field(default=None, foreign_key="user.id")
    receiver_id: Optional[int] = Field(default=None, foreign_key="user.id")
    sender_book_id: Optional[int] = Field(default=None, foreign_key="userbook.id")
    receiver_book_id: Optional[int] = Field(default=None, foreign_key="userbook.id")
    sender_confirm: bool = False
    receiver_confirm: bool = False
    status: str = "pending"

class Offer(OfferDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: Optional[str] = None
    sender: Optional[User] = Relationship(back_populates="sent_offers",
                                          sa_relationship_kwargs={"foreign_keys": "Offer.sender_id"}
                                          )
    receiver: Optional[User] = Relationship(back_populates="received_offers",
                                            sa_relationship_kwargs={"foreign_keys": "Offer.receiver_id"}
                                            )
    sender_book: Optional[UserBook] = Relationship(
        back_populates="sent_offers",
        sa_relationship_kwargs={"foreign_keys": "Offer.sender_book_id"}
    )
    receiver_book: Optional[UserBook] = Relationship(
        back_populates="received_offers",
        sa_relationship_kwargs={"foreign_keys": "Offer.receiver_book_id"}
    )
    exchange: Optional["Exchange"] = Relationship(back_populates="offer")
```
