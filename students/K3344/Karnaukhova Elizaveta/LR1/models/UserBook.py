from sqlmodel import Field, SQLModel, Relationship
from .enums import BookStatus


class UserBook(SQLModel, table=True):
    user_profile_id: int = Field(foreign_key="userprofile.id", primary_key=True)
    book_item_id: int = Field(foreign_key="bookitem.id", primary_key=True)
    status: BookStatus = Field(default=BookStatus.AVAILABLE)

    user_profile: "UserProfile" = Relationship(
        back_populates="books",
        sa_relationship_kwargs={"foreign_keys": "UserBook.user_profile_id"}
    )
    book_item: "BookItem" = Relationship(
        back_populates="owners",
        sa_relationship_kwargs={"foreign_keys": "UserBook.book_item_id"}
    )
