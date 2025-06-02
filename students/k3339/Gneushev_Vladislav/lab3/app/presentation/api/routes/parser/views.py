import aiohttp
from fastapi import APIRouter, HTTPException

from app.presentation.celery.tasks import parse_and_save_bus_types
from app.celery.app import celery_app

router = APIRouter(prefix="/parser", tags=["Parser"])


@router.post("/parse/with-queue")
async def parse_with_queue(
    url: str
):
    try:
        task = parse_and_save_bus_types.delay(url)
        
        return {
            "status": "success",
            "message": "Parsing task started",
            "task_id": task.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parse/with-container")
async def parse_with_container(
    url: str
):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://parser:8001/parse",
                params={"url": url},
                ssl=False
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"API service error: {error_text}"
                    )
                return await response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/parse/status/{task_id}")
async def get_task_status(task_id: str):
    try:
        task = celery_app.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            status = "pending"
        elif task.state == 'SUCCESS':
            status = "completed"
        elif task.state == 'FAILURE':
            status = "failed"
        else:
            status = "in_progress"
            
        return {
            "task_id": task_id,
            "status": status,
            "state": task.state
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
