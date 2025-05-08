from fastapi import FastAPI

from connection import init_db
from api import users, books, libraries, statuses, exchanges


app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"message": "Приложение работает!"}


app.include_router(users.router)
app.include_router(books.router)
app.include_router(libraries.router)
app.include_router(statuses.router)
app.include_router(exchanges.router)
