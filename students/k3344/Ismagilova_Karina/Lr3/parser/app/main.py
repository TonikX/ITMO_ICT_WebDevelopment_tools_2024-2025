from celery.result import AsyncResult
from .celery_worker import celery_app, parse_url_task
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from .parser import parse_and_save_tours

logger = logging.getLogger(__name__)

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")
app = FastAPI()

class InputUrl(BaseModel):
    url: str

@app.post("/parse")
async def parse(data: InputUrl):
    try:
        count = await parse_and_save_tours(data.url)
        return {
            "status": "success",
            "books_parsed": count,
            "message": f"Added {count} new books"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Exception in /parse: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/parse-async")
async def start_parsing(data: InputUrl):
    try:
        logger.info(f"Starting parsing task for URL: {data.url}")
        task = parse_url_task.delay(data.url)
        logger.info(f"Task created with id: {task.id}")

        return {
            "status": "processing",
            "task_id": task.id,
            "message": "Parsing task started successfully",
        }
    except Exception as e:
        logger.error(f"Failed to start task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start parsing task: {str(e)}"
        )

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status": task_result.status,
    }

    if task_result.ready():
        if task_result.successful():
            response["result"] = task_result.result
        else:
            response["error"] = str(task_result.result)

    return response