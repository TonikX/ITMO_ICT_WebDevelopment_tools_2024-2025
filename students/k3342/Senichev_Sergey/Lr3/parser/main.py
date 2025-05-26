import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from celery.result import AsyncResult

from parsers.async_parser import AsyncParser
from celery_app import celery_app, parse_repositories_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GitHub Issues Parser API",
    description="API для парсинга GitHub issues с поддержкой синхронного и асинхронного выполнения",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Схемы запросов и ответов
class ParseRequest(BaseModel):
    repositories: List[str]


class ParseResponse(BaseModel):
    message: str
    status: str
    duration: float = None
    tasks_parsed: int = None
    errors: List[str] = []
    repositories: List[str]


class AsyncParseResponse(BaseModel):
    message: str
    task_id: str
    repositories: List[str]


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: dict = None
    error: str = None


@app.get("/")
def read_root():
    return {
        "message": "GitHub Issues Parser API",
        "version": "1.0.0",
        "endpoints": {
            "parse": "/parse",
            "parse_async": "/parse/async",
            "task_status": "/task/{task_id}",
            "health": "/health"
        }
    }


@app.post("/parse", response_model=ParseResponse)
async def parse_repositories_sync(request: ParseRequest):
    try:
        logger.info(f"Starting synchronous parsing for repositories: {request.repositories}")
        
        parser = AsyncParser()
        result = await parser.run(request.repositories)
        
        return ParseResponse(
            message="Parsing completed successfully",
            status=result["status"],
            duration=result["duration"],
            tasks_parsed=result["tasks_parsed"],
            errors=result["errors"],
            repositories=request.repositories
        )
        
    except Exception as e:
        logger.error(f"Error in synchronous parsing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")


@app.post("/parse/async", response_model=AsyncParseResponse)
def parse_repositories_async(request: ParseRequest):
    try:
        logger.info(f"Starting asynchronous parsing for repositories: {request.repositories}")
        
        task = parse_repositories_task.delay(request.repositories)
        
        return AsyncParseResponse(
            message="Parsing task queued successfully",
            task_id=task.id,
            repositories=request.repositories
        )
        
    except Exception as e:
        logger.error(f"Error starting async parsing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to queue parsing task: {str(e)}")


@app.get("/task/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str):
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        
        if task_result.state == "PENDING":
            response = {
                "task_id": task_id,
                "status": "PENDING",
                "result": None
            }
        elif task_result.state == "PROGRESS":
            response = {
                "task_id": task_id,
                "status": "PROGRESS",
                "result": task_result.info
            }
        elif task_result.state == "SUCCESS":
            response = {
                "task_id": task_id,
                "status": "SUCCESS",
                "result": task_result.result
            }
        else:  # FAILURE
            response = {
                "task_id": task_id,
                "status": "FAILURE",
                "error": str(task_result.info)
            }
            
        return TaskStatusResponse(**response)
        
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "github-parser-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 