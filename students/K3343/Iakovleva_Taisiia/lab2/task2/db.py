from sqlmodel import create_engine, SQLModel

DATABASE_URL = "postgresql://Taisia1@localhost:5432/parseddb"
engine = create_engine(DATABASE_URL)

def init_db():
    SQLModel.metadata.create_all(engine)
