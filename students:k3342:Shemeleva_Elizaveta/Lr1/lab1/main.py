from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import init_db
from routers import tasks, entries, notifications, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
app = FastAPI(title="Time Manager", lifespan=lifespan)

app.include_router(tasks.router)
app.include_router(entries.router)
app.include_router(notifications.router)
app.include_router(users.router)