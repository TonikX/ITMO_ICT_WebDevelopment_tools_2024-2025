import uvicorn
from fastapi import FastAPI

from .connection import *
from .routers import genres
from .routers import users
from .routers import auth
from .routers import books
from .routers import exchanges
from .routers import parsers

app = FastAPI()


@app.get("/")
def hello():
    return "Hello, [username]!"


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(genres.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(exchanges.router)
app.include_router(parsers.router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
