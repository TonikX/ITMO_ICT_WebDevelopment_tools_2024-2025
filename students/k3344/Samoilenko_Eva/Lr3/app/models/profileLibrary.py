from ..schemas.profileLibrary import ProfileLibraryBase
# from app.models.profile import Profile
from ..models.book import Book
from typing import Optional, List
from sqlmodel import Field, Relationship


class ProfileLibrary(ProfileLibraryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner: "Profile" = Relationship(back_populates="library")
    books: List[Book] = Relationship()
