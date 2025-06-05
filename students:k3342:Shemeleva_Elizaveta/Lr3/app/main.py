from fastapi import FastAPI
from sqlmodel import SQLModel
from .database import engine_async
from . import models
from .routers import tasks, entries, notifications, users, parser, parser_async

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    async with engine_async.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

app.include_router(tasks.router)
app.include_router(entries.router)
app.include_router(notifications.router)
app.include_router(users.router)
app.include_router(parser.router)
app.include_router(parser_async.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
