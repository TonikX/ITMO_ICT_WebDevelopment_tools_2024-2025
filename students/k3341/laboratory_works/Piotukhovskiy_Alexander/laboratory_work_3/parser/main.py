from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from config import settings
from db.database import init_db, engine
from parser import save_page
from tasks import parse_url_task, celery_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    engine.dispose()

app = FastAPI(lifespan=lifespan)


class ParseRequest(BaseModel):
    url: str


@app.get("/")
async def hello_world():
    return {"message": "Hello world!"}


@app.post("/parse/async")
async def parse_async(body: ParseRequest):
    await save_page(body.url, prefix="async")
    return {"status": "ok"}


@app.post("/parse/task")
async def parse_celery(body: ParseRequest):
    task = parse_url_task.delay(body.url)
    return {"task_id": task.id}


@app.get("/tasks/{task_id}")
async def task_status(task_id: str):
    res = celery_app.AsyncResult(task_id)
    if res.state == "FAILURE":
        raise HTTPException(500, detail=str(res.result))
    return {"state": res.state}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.app_port)
