from fastapi import FastAPI
from src.api.routers import users, books, userbooks, offers, exchanges, parser_router
from database import init_db

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(users.router)
app.include_router(books.router)
app.include_router(userbooks.router)
app.include_router(offers.router)
app.include_router(exchanges.router)
app.include_router(parser_router.router)
