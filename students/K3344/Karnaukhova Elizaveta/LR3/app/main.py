from fastapi import FastAPI
from .db import init_db
from .endpoints import users, books, exchange, parser

app = FastAPI()

app.include_router(parser.router, tags=["parser"])
app.include_router(users.router)
app.include_router(books.router)
app.include_router(exchange.router)


@app.get("/health")
async def health_check():
    """Эндпоинт для проверки работоспособности сервиса"""
    return {"status": "ok", "message": "Parser API is running"}


@app.on_event("startup")
def on_startup():
    init_db()
