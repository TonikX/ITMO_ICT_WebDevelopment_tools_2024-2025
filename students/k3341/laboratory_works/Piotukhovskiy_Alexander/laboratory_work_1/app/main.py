from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from routes import *
from config import settings
from db.database import engine, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(trip_router, prefix="/trip", tags=["trip"])

@app.get("/")
async def hello_world():
    return {"message": "Hello world!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.app_port)
