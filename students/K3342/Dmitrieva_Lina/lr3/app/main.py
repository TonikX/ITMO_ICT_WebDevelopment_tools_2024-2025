from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from celery.result import AsyncResult
from tasks import run_parser_task
from celery_worker import celery_app

app = FastAPI(title="Парсер через Celery")

class ParserRequest(BaseModel):
    urls: List[str]
    user_id: int
    category_name: str

@app.post("/parse-async")
def parse_async(request: ParserRequest):
    if not request.urls:
        raise HTTPException(status_code=400, detail="Список ссылок пуст")

    task = run_parser_task.delay(request.urls, request.user_id, request.category_name)
    return {"task_id": task.id}

@app.get("/parse-async/{task_id}")
def get_parse_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }
