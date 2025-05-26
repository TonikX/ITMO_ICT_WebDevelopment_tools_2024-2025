import uvicorn
from fastapi import FastAPI

from Lr1.connection import *
from Lr1.routers import genres, exchanges
from Lr1.routers import users, auth, books

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

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
