from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from ..celery_app import celery

router = APIRouter(prefix="/parse_async", tags=["parser_async"])

@router.post("/")
async def parse_async(url: str = Query(...)):
    task = celery.send_task("app.tasks.parse_task", args=[url])
    return JSONResponse({"message": "Task started", "task_id": task.id})
