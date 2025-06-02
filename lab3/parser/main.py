from aiohttp import ClientSession
from bs4 import BeautifulSoup
from fastapi import FastAPI
from pydantic import BaseModel

from celery_app import celery_app
from tasks import parse_url
from celery.result import AsyncResult
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()


class ParseRequest(BaseModel):
    url: str

from celery.result import AsyncResult
from fastapi import Path

@app.get("/result/{task_id}")
def get_task_result(task_id: str = Path(...)):
    result = AsyncResult(task_id, app=celery_app)
    if result.state == "PENDING":
        return {"status": "pending"}
    elif result.state == "SUCCESS":
        return {"status": "success", "result": result.result}
    elif result.state == "FAILURE":
        return {"status": "failure", "error": str(result.result)}
    else:
        return {"status": result.state}

@app.post("/parse")
def parse_endpoint(data: ParseRequest):
    try:
        async_result = parse_url.delay(data.url)
        print(async_result)
        return {"task_id": async_result.id, "status": "queued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
