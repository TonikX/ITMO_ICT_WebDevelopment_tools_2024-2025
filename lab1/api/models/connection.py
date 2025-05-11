from sqlmodel import SQLModel, Session, create_engine

from core.config import settings

import api.models.models

engine = create_engine(settings.DATABASE_URL, echo=True)


def init_db():
    print("Registered tables:", SQLModel.metadata.tables.keys())
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
