from fastapi import FastAPI, HTTPException
import requests
from app.models import ParseRequest
from app.parser_wiki import parse_and_save_single
from app.celery_part import celery
from celery.result import AsyncResult
from app.task import run_parser_task

app = FastAPI()


@app.post("/parse")
def parse_endpoint(request: ParseRequest):
    try:
        destination = parse_and_save_single(request.url)
        return {"message": f"Parsing completed: {destination}"}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")


@app.post("/async_parsing")
def async_parsing(urls: list[str]):
    task = run_parser_task.delay(urls)
    return {"task_id": task.id}


@app.get("/async_parsing/{task_id}")
def async_parsing_result_by_id(task_id: str):
    result = AsyncResult(task_id, app=celery)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }