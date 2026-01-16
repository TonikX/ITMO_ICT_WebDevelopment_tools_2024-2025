from fastapi import FastAPI, HTTPException
import requests
from parser import parse_and_save
from tasks import parse_and_save_task, celery_app
from celery.result import AsyncResult


app = FastAPI()


@app.post("/parse")
async def parse(url: str):
    try:
        await parse_and_save(url)
        return {"message": "Parsing completed!"}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/parse/queue")
async def parse_queue(url: str):
    task = parse_and_save_task.delay(url)
    return {"message": "Task added to queue.", "task_id": task.id}


@app.get("/tasks/{task_id}")
async def read_task(task_id: str):
    res = AsyncResult(task_id, app=celery_app)
    return {"task_id": task_id, "status": res.status, "result": res.result}
