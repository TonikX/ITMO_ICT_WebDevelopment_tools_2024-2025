from fastapi import APIRouter
from tasks import parse_task
from celery.result import AsyncResult
from celery_main import celery_app


router = APIRouter()

@router.post("/async-trigger-parse")
async def async_trigger_parse():
    task = parse_task.delay()
    return {"message": "Parsing started", "task_id": task.id}

@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }
