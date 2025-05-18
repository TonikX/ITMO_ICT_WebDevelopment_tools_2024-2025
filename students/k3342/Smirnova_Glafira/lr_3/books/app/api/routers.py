from fastapi import APIRouter
from app.api.endpoints import auth, books, genres, my_offers, offers, swaps_from, swaps_to, \
    deals, users, parser

router = APIRouter()

router.include_router(parser.router, prefix="/parser", tags=["Parsing"])
router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(books.router, prefix="/books", tags=["Books"])
router.include_router(genres.router, prefix="/genres", tags=["Genres"])
router.include_router(offers.router, prefix="/offers", tags=["Offers"])
router.include_router(my_offers.router, prefix="/offers/mine", tags=["My Offers"])
router.include_router(swaps_to.router, prefix="/swaps/received", tags=["Received Swap Requests"])
router.include_router(swaps_from.router, prefix="/swaps/sent", tags=["Sent Swap Requests"])
router.include_router(deals.router, prefix="/deals", tags=["Deals"])
router.include_router(users.router, prefix="/users", tags=["Users"])







