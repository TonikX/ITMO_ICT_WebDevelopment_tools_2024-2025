from models import SQLModel
from db import engine

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    create_db_and_tables()
