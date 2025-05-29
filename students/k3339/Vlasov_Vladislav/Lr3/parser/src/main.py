from fastapi import FastAPI, HTTPException, requests
from connection import init_db
from tasks import parse_celery
import parser

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.post("/parse")
async def parse(url: str):
    try:
        return await parser.parse(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/parse/celery")
async def start_parse_celery(url: str):
    task = parse_celery.delay(url)
    return {"task_id": task.id}