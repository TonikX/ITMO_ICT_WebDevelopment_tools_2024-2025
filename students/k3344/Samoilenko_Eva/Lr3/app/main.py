from fastapi import FastAPI
from app.crud import profile, book, profileLibrary, exchangeRequest, exchange, user, parser
from app.db.connection import init_db

app = FastAPI()

app.include_router(parser.router, tags=["parser"])
app.include_router(profile.router, tags=["profiles"])
app.include_router(book.router, tags=["books"])
app.include_router(profileLibrary.router, tags=["profile-libraries"])
app.include_router(exchangeRequest.router, tags=["exchange-request"])
app.include_router(exchange.router, tags=["exchange"])
app.include_router(user.router, tags=["user"])


@app.get("/")
def hello():
    return "Hello, eve!"


@app.get("/health")
async def health_check():
    """Эндпоинт для проверки работоспособности сервиса"""
    return {"status": "ok", "message": "Parser API is running"}


@app.on_event("startup")
def on_startup():
    init_db()
