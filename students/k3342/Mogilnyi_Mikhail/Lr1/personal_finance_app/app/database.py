from sqlmodel import SQLModel, create_engine, Session

# Update with your PostgreSQL credentials and database name
DATABASE_URL = "postgresql://user:password@localhost/personal_finance_db"
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
