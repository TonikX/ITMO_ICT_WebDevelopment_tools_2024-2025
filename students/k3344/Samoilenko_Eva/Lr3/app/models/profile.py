from typing import Optional
from sqlmodel import Field, Relationship
from ..schemas.profile import ProfileBase
# from app.models.profileLibrary import ProfileLibrary
# from app.models.user import User


class Profile(ProfileBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    library: Optional["ProfileLibrary"] = Relationship(back_populates="owner")

    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="profile")
