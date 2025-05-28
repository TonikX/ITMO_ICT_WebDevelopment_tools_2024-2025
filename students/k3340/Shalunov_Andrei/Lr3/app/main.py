from fastapi import FastAPI
from app.database import init_db
from app.routers import auth, users, books, exchanges

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    init_db()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(books.router)
app.include_router(exchanges.router)