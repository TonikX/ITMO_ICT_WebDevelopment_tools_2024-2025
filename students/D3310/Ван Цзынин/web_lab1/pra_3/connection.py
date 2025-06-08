import os
from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()
db_url = os.getenv('DB_ADMIN')
engine = create_engine(db_url, echo=True)