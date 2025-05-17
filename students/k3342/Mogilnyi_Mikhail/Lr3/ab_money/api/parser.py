from fastapi import APIRouter, HTTPException
from task2.parse_asyncio import parse_url
router = APIRouter()

from ab_money.celery_worker import run_parser_task

@router.post("/parse")
async def parse_endpoint(url: str):
    try:
        result = await parse_url(url)
        return {"message": "Parsing completed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parse_async")
def parse_async_endpoint(url: str):
    task = run_parser_task.delay(url)
    return {"task_id": task.id}
