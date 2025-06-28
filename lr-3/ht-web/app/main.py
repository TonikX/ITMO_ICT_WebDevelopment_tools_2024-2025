import app.models  # noqa: F401
from fastapi import FastAPI
from app.api import users, auth, books, userbooks, exchanges, parser

app = FastAPI()

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(books.router, prefix="/api/books", tags=["books"])
app.include_router(userbooks.router, prefix="/api/userbooks", tags=["userbooks"])
app.include_router(exchanges.router, prefix="/api/exchanges", tags=["exchanges"])
app.include_router(parser.router, prefix="/api/parser", tags=["parser"])

@app.get("/")
def read_root():
    return {"message": "Book Exchange API"} 