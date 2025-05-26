import asyncio

from fastapi import APIRouter, HTTPException
import requests
from Lr3.book_parser import BookParser
from Lr3.tasks import parse_task

router = APIRouter(prefix="/parsers", tags=["Parsers"])


@router.post("/parse")
def parse(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        parser = BookParser(url=url)
        asyncio.run(parser.run())
        return {"message": "Parsing completed"}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parse/task")
async def parse_task_create(url: str):
    task = parse_task.delay(url)
    return {"task": task.id}


@router.get("/parse/task/{task_id}")
async def get_task(task_id: str):
    task = parse_task.AsyncResult(task_id)
    return {"task": task.id, "status": task.status}
