from sqlmodel import create_engine, Session
from typing import Annotated
from fastapi import Depends

# Подключение к БД
DATABASE_URL = "postgresql://postgres:postgres@db:5432/team_finder"
engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

DBSessionDep = Annotated[Session, Depends(get_session)]