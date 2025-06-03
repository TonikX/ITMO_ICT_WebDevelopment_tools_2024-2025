# UserBook
```python
class UserBookDefault(SQLModel):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    book_id: Optional[int] = Field(default=None, foreign_key="book.id")
    status: BookStatuses

class UserBook(UserBookDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    user: Optional[User] = Relationship(back_populates="books")
    book: Optional[Book] = Relationship(back_populates="user_books")
    sent_offers: List["Offer"] = Relationship(
        back_populates="sender_book",
        sa_relationship_kwargs={"foreign_keys": "Offer.sender_book_id"}
    )
    received_offers: List["Offer"] = Relationship(
        back_populates="receiver_book",
        sa_relationship_kwargs={"foreign_keys": "Offer.receiver_book_id"}
    )
```
