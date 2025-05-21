from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import async_
from celery_worker import parse_from_url, celery_app
from run import extract_user_links 


app = FastAPI(title="Parser Service")

class ParseRequest(BaseModel):
    url: str

@app.post("/parse")
async def parse_users(request: ParseRequest):
    try:
        user_links = await extract_user_links(request.url)
        if not user_links:
            return {"message": "No user links found"}

        await async_.main(user_links)
        return {"message": f"Parsed {len(user_links)} users"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/parse/trigger")
async def trigger_parse(request: ParseRequest):
    task = parse_from_url.delay(request.url)
    return {"message": "Parsing started", "task_id": task.id}


@app.get("/parse/status/{task_id}")
async def get_task_status(task_id: str):
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
        "successful": result.successful() if result.ready() else None
    }