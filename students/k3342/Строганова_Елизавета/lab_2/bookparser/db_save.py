from sqlmodel import Session
from models.models import Book
from connection.db import engine

def save_books(books):
    with Session(engine) as session:
        for book in books:
            session.add(Book(**book))
        session.commit()
