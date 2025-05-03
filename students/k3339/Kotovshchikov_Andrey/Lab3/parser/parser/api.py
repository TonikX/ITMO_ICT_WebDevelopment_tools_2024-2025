from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from parser.asyncio import parse_and_save
from parser.tasks import parse_and_save_async
from parser.logger import setup_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/parse", status_code=status.HTTP_200_OK)
async def parse(url: str):
    await parse_and_save(url)
    return {"message": "ok"}


@app.post("/parse/async", status_code=status.HTTP_200_OK)
async def parse(url: str):
    parse_and_save_async.delay(url)
    return {"message": "ok"}
