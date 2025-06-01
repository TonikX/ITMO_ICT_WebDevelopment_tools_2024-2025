from fastapi import APIRouter, Body
from celery.result import AsyncResult
from fastapi import HTTPException
from pydantic import BaseModel
from tasks import parse_task

router = APIRouter()

class ParseRequest(BaseModel):
    url: str

@router.post("/parse-async")
async def parse_async(request: ParseRequest = Body(...)):
    task = parse_task.delay(request.url)
    return {
        "task_id": task.id,
        "status": "queued",
        "url": request.url
    }


@router.get("/parse-status/{task_id}")
async def get_parse_status(task_id: str):
    task = AsyncResult(task_id)
    if not task.ready():
        return {
            "task_id": task_id,
            "status": task.status
        }

    if task.failed():
        raise HTTPException(
            status_code=400,
            detail=f"Task failed: {task.result.get('message', 'Unknown error')}"
        )

    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result
    }