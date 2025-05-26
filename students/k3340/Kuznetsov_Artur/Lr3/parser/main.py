from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from async_parse import main as async_parse
from connection import init_db
from multiprocessing_parse import main as multiprocessing_parse
from celery_app import celery_app
from tasks import parse_async_task, parse_mp_task, parse_threading_task
from threading_parse import main as threading_parse

app = FastAPI()


class ParseRequest(BaseModel):
    urls: list[str]


@app.on_event("startup")
def startup_event():
    init_db()


@app.post("/parse/threading")
def parse_threading(request: ParseRequest):
    try:
        threading_parse(request.urls)
        return {"message": "Threading parsing completed"}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))


@app.post("/parse/multiprocessing")
def parse_multiprocessing(request: ParseRequest):
    try:
        multiprocessing_parse(request.urls)
        return {"message": "Multiprocessing parsing completed"}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))


@app.post("/parse/async")
async def parse_async(request: ParseRequest):
    try:
        await async_parse(request.urls)
        return {"message": "Async parsing completed"}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))


@app.post("/queue/parse/threading")
def queue_threading(request: ParseRequest):
    task = parse_threading_task.delay(request.urls)
    return {"task_id": task.id}


@app.post("/queue/parse/multiprocessing")
def queue_mp(request: ParseRequest):
    task = parse_mp_task.delay(request.urls)
    return {"task_id": task.id}


@app.post("/queue/parse/async")
def queue_async(request: ParseRequest):
    task = parse_async_task.delay(request.urls)
    return {"task_id": task.id}


@app.get("/queue/status/{task_id}")
def get_status(task_id: str):
    res = celery_app.AsyncResult(task_id)
    return {"status": res.status, "result": res.result}
