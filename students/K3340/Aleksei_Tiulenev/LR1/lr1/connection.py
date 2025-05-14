import os
from dotenv import load_dotenv
from sqlmodel import Session, create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
db_url = os.getenv('DB_URL')
engine = create_engine(db_url, echo=True)


SessionLocal = sessionmaker(
    bind=engine, 
    class_=Session, 
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)
