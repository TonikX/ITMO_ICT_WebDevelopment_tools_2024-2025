from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.tasks import parse_news_task

router = APIRouter()

class ParseRequest(BaseModel):
    count: int = Field(ge=1, le=200, description="Сбор новостей")

@router.post("/parse")
def start_parse(req: ParseRequest):
    try:
        task = parse_news_task.delay(req.count)
        return {"message": "Parsing started", "task_id": task.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/parse/status/{task_id}")
def get_parse_status(task_id: str):
    try:
        task = parse_news_task.AsyncResult(task_id)
        return {"task_id": task_id, "status": task.status, "result": task.result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))