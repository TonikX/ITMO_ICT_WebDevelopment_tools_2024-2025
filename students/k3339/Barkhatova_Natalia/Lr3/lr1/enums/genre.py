from enum import Enum


class BookGenre(str, Enum):
    fiction = "fiction"
    nonfiction = "nonfiction"
    mystery = "mystery"
    fantasy = "fantasy"
    science_fiction = "science_fiction"
    biography = "biography"
    history = "history"
    romance = "romance"
    thriller = "thriller"
    children = "children"
    self_help = "self_help"
    poetry = "poetry"
    classic = "classic"
    other = "other"
