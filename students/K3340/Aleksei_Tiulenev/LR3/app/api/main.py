from fastapi import FastAPI, HTTPException
import requests
from app.worker.celery_worker import parse_url_task
from app.schemas.parser import ParseRequest, TaskResponse

app = FastAPI(title="URL Parser API")

@app.post("/parse/sync", response_model=TaskResponse)
async def parse_sync(request: ParseRequest):
    """
    Synchronous endpoint that calls the parser service directly
    """
    try:
        response = requests.post(
            'http://parser:8001/parse',
            json={'url': request.url}
        )
        response.raise_for_status()
        return TaskResponse(
            message="Parsing completed successfully",
            result=response.json()
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/parse/async", response_model=TaskResponse)
async def parse_async(request: ParseRequest):
    """
    Asynchronous endpoint that uses Celery to parse the URL
    """
    try:
        task = parse_url_task.delay(request.url)
        return TaskResponse(
            task_id=task.id,
            message="Parsing task submitted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/parse/status/{task_id}", response_model=TaskResponse)
async def get_parse_status(task_id: str):
    """
    Get the status of an asynchronous parsing task
    """
    try:
        task = parse_url_task.AsyncResult(task_id)
        if task.ready():
            return TaskResponse(
                task_id=task_id,
                message="Task completed",
                result=task.get()
            )
        return TaskResponse(
            task_id=task_id,
            message="Task is still processing"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 