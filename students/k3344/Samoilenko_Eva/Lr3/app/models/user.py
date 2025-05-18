from typing import Optional
from sqlmodel import Field, Relationship

# from app.schemas.user import UserBase
# from app.models.profile import Profile

#
# class User(UserBase, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     hashed_password: str
#
#     # Связь один-к-одному с Profile
#     profile: Optional["Profile"] = Relationship(back_populates="user")
