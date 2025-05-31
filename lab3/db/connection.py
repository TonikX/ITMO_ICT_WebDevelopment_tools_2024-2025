from sqlmodel import SQLModel, Session, create_engine
from config.secrets import DATABASE_DSN

engine = create_engine(DATABASE_DSN, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
