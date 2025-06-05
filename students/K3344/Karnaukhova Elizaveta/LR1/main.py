from fastapi import FastAPI
from .db import init_db
from .endpoints import users, books, exchange

app = FastAPI()

app.include_router(users.router)
app.include_router(books.router)
app.include_router(exchange.router)


@app.get("/")
def hello():
    return "Hello, LIZA!"


@app.on_event("startup")
def on_startup():
    init_db()
