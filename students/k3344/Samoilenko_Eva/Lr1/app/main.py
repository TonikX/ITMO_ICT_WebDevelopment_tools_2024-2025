from fastapi import FastAPI
from .db.connection import init_db
from .crud import profile, book, profileLibrary, exchangeRequest, exchange, user


app = FastAPI()

app.include_router(profile.router, tags=["profiles"])
app.include_router(book.router, tags=["books"])
app.include_router(profileLibrary.router, tags=["profile-libraries"])
app.include_router(exchangeRequest.router, tags=["exchange-request"])
app.include_router(exchange.router, tags=["exchange"])
app.include_router(user.router, tags=["user"])


@app.get("/")
def hello():
    return "Hello, eve!"


@app.on_event("startup")
def on_startup():
    init_db()


test_db = [
    {
        "id": 1,
        "username": "sam",
        "bio": "люблю поплакать и посмеяться вместе с героями книг",
        "skills": ["Чтение", "Каллиграфия"],
        "experience": "5 лет",
        "preferences": "Фантастика",
        "books": [
            {
                "id": 1,
                "title": "1984",
                "author": "Джордж Оруэлл",
                "description": "Антиутопия",
                "owner_id": 1
            }
        ]
    },
    {
        "id": 2,
        "username": "bob",
        "bio": "Собиратель очччень редких изданий",
        "skills": ["Поиск книг", "Коллекционирование"],
        "experience": "11 лет",
        "preferences": "Классика",
        "books": [
            {
                "id": 2,
                "title": "Преступление и наказание",
                "author": "Ф.М. Достоевский",
                "description": "Русская классика",
                "owner_id": 2
            }
        ]
    }
]
