from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

from api import users, books, user_books, exchanges, auth
from models import SQLModel
from db import engine

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(books.router)
app.include_router(user_books.router)
app.include_router(exchanges.router)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)