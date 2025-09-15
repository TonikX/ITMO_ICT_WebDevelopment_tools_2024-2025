from sqlmodel import SQLModel, Field, create_engine
from sqlalchemy.orm import Session
from sqlalchemy import text
#from app.models import Task
from app.models import Task

DATABASE_URL = "postgresql://postgres:1234@localhost/time_manager_db"
engine = create_engine(DATABASE_URL)

def get_session():
    return Session(engine)

def clear_tasks():
    with get_session() as session:
        session.execute(text('DELETE FROM task'))
        session.commit()