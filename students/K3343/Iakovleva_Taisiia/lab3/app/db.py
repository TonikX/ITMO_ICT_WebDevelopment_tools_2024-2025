from sqlmodel import SQLModel, create_engine, Session
from models import ParsedPage

DATABASE_URL = "postgresql://postgres:postgres@db/finance"


engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def save_parsed_page(url: str, title: str):
    with Session(engine) as session:
        page = ParsedPage(url=url, title=title)
        session.add(page)
        session.commit()
