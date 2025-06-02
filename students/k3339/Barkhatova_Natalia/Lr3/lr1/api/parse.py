from fastapi import APIRouter

from tasks import parse_url_task

router = APIRouter()

PARSER_URL = "http://parser:8000"


@router.get("/parse")
def parse_async(url: str):
    task = parse_url_task.delay(url)
    return {"message": "Task submitted", "task_id": task.id}
