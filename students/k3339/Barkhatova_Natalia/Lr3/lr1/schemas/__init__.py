from schemas.book import Book, BookShort
from schemas.exchange import Exchange
from schemas.user import User, UserShort
from schemas.review import Review
from schemas.location import Location

Book.update_forward_refs(Exchange=Exchange)
Exchange.update_forward_refs(BookShort=BookShort, UserShort=UserShort)
User.update_forward_refs(Book=Book, Review=Review, Location=Location)
Review.update_forward_refs(User=User)
Location.update_forward_refs()
