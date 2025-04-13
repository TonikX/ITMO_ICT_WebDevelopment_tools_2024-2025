from sqlmodel import SQLModel, Session, select

from app.db.genres import DEFAULT_GENRES
from app.models import *
from app.db.session import engine

def init_db():
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        statement = select(Genre)
        existing_genres = session.exec(statement).all()

        if not existing_genres:
            for name in DEFAULT_GENRES:
                session.add(Genre(name=name))
            session.commit()