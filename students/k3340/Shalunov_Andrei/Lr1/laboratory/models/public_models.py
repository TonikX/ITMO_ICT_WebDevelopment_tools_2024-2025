from .default_models import ProfileDefault, BookDefault

class ProfilePublic(ProfileDefault):
    id: int

class BookPublic(BookDefault):
    id: int
