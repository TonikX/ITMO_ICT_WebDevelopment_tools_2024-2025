from fastapi import APIRouter
from fastapi import FastAPI, Depends

from api import auth
from api.crud import book, review, user, location, exchange
from db import init_db
from security.token_service import get_current_user

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(auth.router)

protected_router = APIRouter(
    dependencies=[Depends(get_current_user)]
)

protected_router.include_router(user.router)
protected_router.include_router(book.router)
protected_router.include_router(exchange.router)
protected_router.include_router(review.router)
protected_router.include_router(location.router)

app.include_router(protected_router)
