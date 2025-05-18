from celery.result import AsyncResult
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .celery_worker import parse_url_task, celery_app
from .parser import async_parse

app = FastAPI()

class URLInput(BaseModel):
    url: str

@app.post("/parse")
def trigger_parse_task(data: URLInput):
    if not data.url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL")
    task = parse_url_task.delay(data.url)
    return {"message": "Task submitted", "task_id": task.id}

@app.get("/task-status/{task_id}")
def get_task_status(task_id: str):
    task = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task.id,
        "status": task.status,
        "result": task.result if task.successful() else None
    }

@app.post("/parse-direct")
async def parse_direct(data: URLInput):
    try:
        count = await async_parse(data.url)
        return {"message": "Парсинг завершён", "added": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка парсинга: {e}")