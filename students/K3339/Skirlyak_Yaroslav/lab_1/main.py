from contextlib import asynccontextmanager
from fastapi import FastAPI

from connection import init_db
from controller import author, book, category, user, sharing, book_copy

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(author.router)
app.include_router(category.router)
app.include_router(book.router)
app.include_router(user.router)
app.include_router(book_copy.router)
app.include_router(sharing.router)