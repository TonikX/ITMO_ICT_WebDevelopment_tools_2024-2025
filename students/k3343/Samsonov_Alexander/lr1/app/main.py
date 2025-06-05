from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from app.users import users

app = FastAPI()
app.include_router(users.router)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
