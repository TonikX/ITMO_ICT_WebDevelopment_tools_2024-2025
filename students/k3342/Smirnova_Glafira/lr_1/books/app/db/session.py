from sqlmodel import Session, create_engine

from app.core.config import settings

engine = create_engine(settings.DB_ADMIN, echo=False)

def get_session():
    with Session(engine) as session:
        yield session