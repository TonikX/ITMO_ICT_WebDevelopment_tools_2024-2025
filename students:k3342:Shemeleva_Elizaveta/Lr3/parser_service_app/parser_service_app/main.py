from fastapi import FastAPI, HTTPException
import aiohttp
from sqlmodel import SQLModel
from .database import engine_async
from .async_parser import parse_itmo, parse_spbpu, parse_expoforum, init_db
from .models import Task
from .database import AsyncSessionLocal

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    async with engine_async.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

@app.post("/parse")
async def parse_endpoint(url: str):
    if "student.itmo.ru" in url:
        parser = parse_itmo
    elif "www.spbstu.ru" in url:
        parser = parse_spbpu
    elif "www.expoforum.ru" in url:
        parser = parse_expoforum
    else:
        raise HTTPException(status_code=400, detail="Unsupported URL")

    async with aiohttp.ClientSession() as session:
        events = await parser(session, url)

    return {
        "events": [
            {"description": e.description, "due_date": e.due_date, "priority": e.priority.value}
            for e in events
        ]
    }
