from fastapi import FastAPI, Depends

from api.dependency import get_current_user
from api.endpoints import book
from api.endpoints.book import book_router
from api.endpoints.exchangeRequest import exchange_request_router
from api.endpoints.genre import genre_router
from api.endpoints.user import user_router, user_protected_router
from api.models.connection import init_db
from api.services.service import services_router

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(user_protected_router, prefix="/user", tags=["User"])
app.include_router(book_router, prefix="/book", tags=["Book"], dependencies=[Depends(get_current_user)])
app.include_router(genre_router, prefix="/genre", tags=["Genre"], dependencies=[Depends(get_current_user)])
app.include_router(exchange_request_router, prefix="/exchange_request", tags=["Exchange Request"],
                   dependencies=[Depends(get_current_user)])
app.include_router(services_router, prefix="/services", tags=["Services"], dependencies=[Depends(get_current_user)])
