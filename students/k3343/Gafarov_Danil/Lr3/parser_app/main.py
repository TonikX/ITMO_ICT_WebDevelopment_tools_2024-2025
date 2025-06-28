from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import aiohttp
from sqlmodel import SQLModel, Field, create_engine
from sqlalchemy.orm import Session

app = FastAPI()

# Модель для входящих данных
class ParseRequest(BaseModel):
    url: str

# Модель пользователя
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True)

# Подключение к БД
DATABASE_URL = "postgresql://postgres:postgres@db:5432/team_finder"
engine = create_engine(DATABASE_URL)

def get_session():
    return Session(engine)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.post("/parse")
async def run_parser(req: ParseRequest):
    async with aiohttp.ClientSession() as session:
        data = await fetch(session, req.url)

    users = extract_users(data)
    saved = save_to_db(users)

    return {"saved": saved}

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()

def extract_users(data):
    return [{
        "email": item["email"],
        "username": item["login"]["username"]
    } for item in data.get("results", [])]

def save_to_db(users):
    with get_session() as session:
        existing_emails = [u.email for u in session.query(User).all()]
        new_users = [User(**u) for u in users if u["email"] not in existing_emails]
        session.add_all(new_users)
        session.commit()
        return len(new_users)