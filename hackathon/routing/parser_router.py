from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from celery_worker import parse_url_tasks, parse_all_urls, celery_app

router = APIRouter()


@router.post("/parse-all")
def parse_all():
    try:
        task = parse_all_urls.delay()
        return {"task_id": task.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parse-url")
def parse_url(url: str):
    try:
        task = parse_url_tasks.delay(url)
        return {"task_id": task.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task-status/{task_id}")
def get_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.ready():
        return {"status": "completed", "result": task_result.result}
    return {"status": "pending"}
